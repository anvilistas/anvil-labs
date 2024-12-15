# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import wraps as _wraps

import anvil.server as _server
from anvil import is_server_side

__version__ = "0.0.1"

PRIVATE_NAME = "anvil-labs.private.batch_call"

_registered = {}


def _has_permission(require_user):
    if require_user is None:
        return True

    import anvil.users

    user = anvil.users.get_user()
    if user is None:
        msg = "You must be logged in to call this server function"
        raise anvil.users.AuthenticationFailed(msg)

    if require_user is True:
        return True

    return require_user(user)


def _wrap_require(fn, name, require_user):
    @_wraps(fn)
    def require_wrapper(*args, **kws):
        if not _has_permission(require_user):
            msg = f"You do not have permission to call server function '{name}'"
            raise _server.PermissionDenied(msg)
        return fn(*args, **kws)

    return require_wrapper


def _register(fn, name=None, require_user=None):
    if name is None:
        name = fn.__name__
    _registered[name] = _wrap_require(fn, name, require_user)
    return fn


def _do_batch_call(call_sigs):
    rv = []
    for fn_name, args, kws in call_sigs:
        try:
            fn = _registered[fn_name]
        except KeyError:
            raise _server.NoServerFunctionError(
                f"No server batchable function matching '{fn_name}' has been registered"
            )
        rv.append(fn(*args, **kws))

    if len(call_sigs) > 1:
        return rv
    else:
        return rv[0]


if is_server_side():
    _server.callable(PRIVATE_NAME)(_do_batch_call)


def callable(fn_or_name=None, require_user=None):
    if fn_or_name is None or isinstance(fn_or_name, str):
        _callable_decorator = _server.callable(fn_or_name, require_user=require_user)
        return lambda fn: _callable_decorator(_register(fn, fn_or_name, require_user))

    return _server.callable(_register(fn_or_name))


class batch_call:
    @staticmethod
    def server_call(*args, **kws):
        return _server.call(PRIVATE_NAME, *args, **kws)

    @staticmethod
    def server_call_s(*args, **kws):
        return _server.call_s(PRIVATE_NAME, *args, **kws)

    def __init__(self, *, silent=False):
        self._result = None
        self._silent = silent
        self._sigs = []
        self._enter = False
        self._exit = False

    def call(self, fn_name, *args, **kws):
        self._sigs.append([fn_name, args, kws])

    @property
    def result(self):
        if not self._exit:
            raise RuntimeError(
                "accessing result inside batch_call context is not allowed"
            )
        return self._result

    def __enter__(self):
        if self._enter:
            raise RuntimeError("cannot re-execute a batched call")
        self._enter = True
        return self

    def __exit__(self, exc_type, *exc_args):
        self._exit = True
        sigs, self._sigs = self._sigs, []

        if exc_type:
            # an exception was raised inside the context
            return

        call_method = self.server_call_s if self._silent else self.server_call

        if sigs:
            self._result = call_method(sigs)


def batch_call_s():
    return batch_call(silent=True)
