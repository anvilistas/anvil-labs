# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import partial as _partial

from anvil.js import await_promise as _await_promise
from anvil.js import window as _W
from anvil.server import call_s as _call_s

__version__ = "0.0.1"

_sentinel = object()
try:
    # just for a nice repr by default
    _call_s.__name__ = "call_s"
    _call_s.__qualname__ = "anvil.server.call_s"
except AttributeError:
    pass

# python errors get wrapped when called from a js function in python
# so instead reject the error from a js function in js
_promise_handler = _W.Function(
    "fn",
    """
return (resolve, reject) => {
    try {
        resolve(fn());
    } catch (e) {
        reject(e);
    }
}
""",
)


class AsyncCall:
    def __init__(self, fn, *args, **kws):
        fn = _partial(fn, *args, **kws)
        self._orig = fn
        self._update_promise(fn)

    def on_result(self, result_handler, error_handler=None):
        self._update_promise(self._get_new_fn(result_handler, error_handler))
        return self

    def on_error(self, error_handler):
        self._update_promise(self._get_new_fn(None, error_handler))
        return self

    def _update_promise(self, fn):
        self._promise = _W.Promise(_promise_handler(fn))

    def _get_new_fn(self, result_handler=None, error_handler=None):
        def new_fn():
            res = err = _sentinel
            try:
                res = _await_promise(self._promise)
            except Exception as e:
                err = e
            if res is not _sentinel:
                if result_handler is None:
                    return res
                else:
                    return result_handler(res)
            elif error_handler:
                return error_handler(err)
            else:
                raise err

        return new_fn

    def wait(self):
        return _await_promise(self._promise)

    def __repr__(self):
        fn_repr = repr(self._orig).replace("functools.partial", "")
        return f"<non_blocking.AsyncCall{fn_repr}>"


def call_async(fn, *args, **kws):
    "call a function in a non-blocking way"
    assert callable(fn), "the first argument must be a callable that takes no args"
    return AsyncCall(fn, *args, **kws)


def call_server_async(fn_name, *args, **kws):
    "call a server function in a non_blocking way"
    if not type(fn_name) is str:
        raise TypeError("the first argument must be the server function name as a str")
    return AsyncCall(_call_s, fn_name, *args, **kws)


def wait_for(async_call_object):
    "wait for a non-blocking function to complete its execution"
    if not isinstance(async_call_object, AsyncCall):
        raise TypeError(
            f"expected an AsyncCall object, got {type(async_call_object).__name__}"
        )
    return async_call_object.wait()


class Interval:
    """create an interval - T
    he first argument must a function that takes no arguments
    The second argument is the delay in seconds.
    The funciton will be called every delay seconds.
    To stop the interval either set its interval to None or 0 or call the clear_interval() method
    """

    def __init__(self, fn, delay=None):
        assert callable(
            fn
        ), "the first argument to interval must be a callable that takes no arguments"
        self._id = None
        self._fn = fn
        self.interval = delay

    @property
    def interval(self):
        return self._delay

    @interval.setter
    def interval(self, value):
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError(f"cannot set interval to be of type {type(value).__name__}")
        self._delay = value
        _W.clearInterval(self._id)
        if not value:
            return
        self._id = _W.setInterval(self._fn, value * 1000)

    def clear_interval(self):
        self.interval = None
