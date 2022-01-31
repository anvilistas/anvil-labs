# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import partial as _partial

from anvil.js import window as _W
from anvil.server import call_s as _call_s

__version__ = "0.0.1"

try:
    # just for a nice repr by default
    _call_s.__name__ = "call_s"
    _call_s.__qualname__ = "anvil.server.call_s"
except AttributeError:
    pass

# python errors get wrapped when called from a js function in python
# so instead reject the error from a js function in js
_deferred = _W.Function(
    "fn",
    """
const deferred = { };
const result = new Promise((resolve, reject) => {
    try {
        resolve(fn);
        deferred.status = "FULFILLED";
    } catch (e) {
        reject(e);
        deferred.status = "REJECTED";
    }
});
let handledResult = result;

return Object.assign(deferred, {
    status: "PENDING",
    result,
    on_result(handleResult, handleError) => {
        handledResult = handledResult.then(handleResult, handleError);
    },
    on_error(handleError) => {
        handledResult = handledResult.catch(handleError);
    },
    await_result: async () => await result;
});
""",
)


class AsyncCall:
    def __init__(self, fn, *args, **kws):
        self._fn = _partial(fn, *args, **kws)
        self._deferred = _deferred(self._fn)

    @property
    def result(self):
        return self._deferred.result

    def get_status(self):
        return self._deferred.status

    def on_result(self, result_handler, error_handler=None):
        self._deferred.on_result(result_handler, error_handler)
        return self

    def on_error(self, error_handler):
        self._deferred.on_error(error_handler)
        return self

    def await_result(self):
        return self._deferred.result

    wait = await_result

    def __repr__(self):
        fn_repr = repr(self._fn).replace("functools.partial", "")
        return f"<non_blocking.AsyncCall{fn_repr}>"


def call_async(fn, *args, **kws):
    "call a function in a non-blocking way"
    if not callable(fn):
        raise TypeError("the first argument must be a callable")
    return AsyncCall(fn, *args, **kws)


def call_server_async(fn_name, *args, **kws):
    "call a server function in a non_blocking way"
    if not isinstance(fn_name, str):
        raise TypeError("the first argument must be the server function name as a str")
    return AsyncCall(_call_s, fn_name, *args, **kws)


def wait_for(async_call_object):
    "wait for a non-blocking function to complete its execution"
    if not isinstance(async_call_object, AsyncCall):
        raise TypeError(
            f"expected an AsyncCall object, got {type(async_call_object).__name__}"
        )
    return async_call_object.await_result()


class AbstractTimer:
    _clearer = None
    _setter = None
    _prop = None

    def __init__(self, fn, delay=None):
        assert callable(
            fn
        ), f"the first argument to {type(self).__name__} must be a callable that takes no arguments"
        self._id = None
        self._fn = fn
        self.delay = delay

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError(
                f"cannot set {self._prop} to be of type {type(value).__name__}"
            )
        self._clearer(self._id)
        self._delay = value
        if value is None:
            return
        self._id = self._setter(self._fn, value * 1000)

    def _clear(self):
        """Stop the timer from running"""
        self.delay = None


class Interval(AbstractTimer):
    """create an interval
    The first argument must a function that takes no arguments
    The second argument is the interval in seconds.
    The funciton will be called every interval seconds.
    To stop the interval either set its interval to None or 0 or call the clear_interval() method
    """

    _clearer = _W.clearInterval
    _setter = _W.setInterval
    _prop = "interval"

    def __init__(self, fn, interval=None):
        super().__init__(fn, interval)

    interval = AbstractTimer.delay
    clear_interval = AbstractTimer._clear


class Timeout(AbstractTimer):
    """create an timeout
    The first argument must a function that takes no arguments
    The second argument is the delay in seconds.
    The funciton will be called after delay seconds.
    To stop the function from being called either set the delay to None
    or set the delay to a new value.
    """

    _clearer = _W.clearTimeout
    _setter = _W.setTimeout
    _prop = "delay"

    clear_timeout = AbstractTimer._clear
