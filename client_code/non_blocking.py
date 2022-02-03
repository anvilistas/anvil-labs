# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import partial as _partial

from anvil.js import report_exceptions as _report
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
const deferred = {status: "PENDING", error: null};
const p = deferred.promise = new Promise(async (resolve, reject) => {
    try {
        resolve(await fn());
        deferred.status = "FULFILLED";
    } catch (e) {
        deferred.status = "REJECTED";
        deferred.error = e;
        reject(e);
    }
});

let handledResult = p;
let handledError = null;

return Object.assign(deferred, {
    on_result(resultHandler, errorHandler) {
        if (!errorHandler && handledError) {
            // the on_error was already called so provide a dummy handler;
            errorHandler = () => {};
        }
        handledResult = p.then(resultHandler, errorHandler);
        handledError = null;
    },
    on_error(errorHandler) {
        handledError = handledResult.catch(errorHandler);
        handledResult = p;
    },
    await_result: async () => await p,
});
""",
)


class _Result:
    # dicts may come back as javascript object literals
    # so wrap the results in a more opaque python object
    def __init__(self, value):
        self.value = value

    @staticmethod
    def wrap(fn):
        def wrapper():
            return _Result(fn())

        return wrapper

    @staticmethod
    def unwrap(fn):
        def unwrapper(res):
            return fn(res.value)

        return unwrapper


class _AsyncCall:
    def __init__(self, fn, *args, **kws):
        self._fn = _partial(fn, *args, **kws)
        self._deferred = _deferred(_Result.wrap(self._fn))

    def _check_pending(self):
        if self._deferred.status == "PENDING":
            raise RuntimeError("the async call is still pending")

    @property
    def result(self):
        """If the function call is not complete, returns a Promise
        If the function call is complete:
        Returns: the return value from the function call
        Raises: the error raised by the function call
        """
        self._check_pending()
        return self.await_result()

    @property
    def error(self):
        """Returns the error raised by the function call, else None"""
        self._check_pending()
        return self._deferred.error

    @property
    def status(self):
        """Returns: 'PENDING', 'FULFILLED', 'REJECTED'"""
        return self._deferred.status

    def on_result(self, result_handler, error_handler=None):
        error_handler = error_handler and _report(error_handler)
        result_handler = _Result.unwrap(_report(result_handler))
        self._deferred.on_result(result_handler, error_handler)
        return self

    def on_error(self, error_handler):
        self._deferred.on_error(_report(error_handler))
        return self

    def await_result(self):
        return self._deferred.await_result().value

    def __repr__(self):
        fn_repr = repr(self._fn).replace("functools.partial", "")
        return f"<non_blocking.AsyncCall{fn_repr}>"


# deprecated
_AsyncCall.wait = _AsyncCall.await_result


def call_async(fn, *args, **kws):
    "call a function in a non-blocking way"
    if not callable(fn):
        raise TypeError("the first argument must be a callable")
    return _AsyncCall(fn, *args, **kws)


def call_server_async(fn_name, *args, **kws):
    "call a server function in a non_blocking way"
    if not isinstance(fn_name, str):
        raise TypeError("the first argument must be the server function name as a str")
    return _AsyncCall(_call_s, fn_name, *args, **kws)


def wait_for(async_call_object):
    "wait for a non-blocking function to complete its execution"
    if not isinstance(async_call_object, _AsyncCall):
        raise TypeError(
            f"expected an AsyncCall object, got {type(async_call_object).__name__}"
        )
    return async_call_object.await_result()


class _AbstractTimer:
    _clearer = None
    _setter = None

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
            raise TypeError(f"cannot set delay to be of type {type(value).__name__}")
        self._clearer(self._id)
        self._delay = value
        if value is None:
            return
        self._id = self._setter(self._fn, value * 1000)

    def clear(self):
        """Stop the function from executing"""
        self.delay = None


class Interval(_AbstractTimer):
    """Create an interval
    The first argument must be a function that takes no arguments
    The second argument is the delay in seconds.
    The function will be called every delay seconds.
    To stop the interval either set its delay to None or call the clear() method
    """

    def __init__(self, fn, delay=None):
        super().__init__(fn, delay)

    _clearer = _W.clearInterval
    _setter = _W.setInterval


class Timeout(_AbstractTimer):
    """Create a timeout
    The first argument must be a function that takes no arguments
    The second argument is the delay in seconds.
    The function will be called after delay seconds.
    To stop the function from being called either set the delay to None or call the clear() method
    Setting a new delay value stops the pending function, which will now be called after the new delay seconds.
    """

    def __init__(self, fn, delay=None):
        super().__init__(fn, delay)

    _clearer = _W.clearTimeout
    _setter = _W.setTimeout


if __name__ == "__main__":
    # TESTS
    from time import sleep as _sleep

    _v = 0

    def _f():
        global _x, _v
        _v += 1
        if _v >= 5:
            _x.delay = None

    print("Testing Interval")
    _x = Interval(_f)
    assert _v == 0
    _x.delay = 0.01
    _sleep(0.1)
    assert _v == 5
    _x.delay = 0.01
    assert _v == 5
    _sleep(0.1)
    assert _v == 6

    print("Testing Timeout")
    _v = 0
    _x = Timeout(_f, delay=0.05)
    _sleep(0.01)
    _x.delay = 0.05
    _sleep(0.1)
    assert _v == 1

    print("Testing Async Call")
    _x = call_async(lambda v: v + 1, 42)
    assert _x.status == "PENDING"
    try:
        _x.result
    except RuntimeError:
        pass
    else:
        assert False
    _v = _x.await_result()
    assert _x.status == "FULFILLED"
    assert _x.result == 43
    assert _x.error is None
    _v = None

    def _f(v):
        global _v
        _v = v

    _x.on_result(_f)
    assert _v is None
    _sleep(0)
    assert _v == 43
    _v = None
    _x = call_async(lambda v: v + 1, "foo")
    _x.on_result(_f)
    _x.on_error(_f)
    _sleep(0)
    assert _x.status == "REJECTED"
    assert isinstance(_v, TypeError)
    assert _v is _x.error
    try:
        _x.result
    except TypeError:
        pass
    else:
        assert False
    _v = call_async(lambda: {}).await_result()
    assert type(_v) is dict
    print("PASSED")
