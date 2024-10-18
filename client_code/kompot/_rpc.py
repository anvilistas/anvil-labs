# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import json as _json
from functools import wraps as _wraps

import anvil.server as _server

from ._serialize import UNHANDLED, reconstruct, serialize

__version__ = "0.0.1"

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


def _dumps(obj):
    serialized = serialize(obj)
    unhandled = serialized.pop(UNHANDLED)
    return _json.dumps(serialized), unhandled


def _loads(serialized, unhandled):
    obj = _json.loads(serialized)
    obj[UNHANDLED] = unhandled
    return reconstruct(obj)


def _wrap_callable(fn):
    @_wraps(fn)
    def wrapped(json_obj, unhandled):
        args, kws = _loads(json_obj, unhandled)
        rv = fn(*args, **kws)
        return _dumps(rv)

    return wrapped


def call(fn_name, *args, **kws):
    rv = _server.call(fn_name, *_dumps([args, kws]))
    return _loads(*rv)


def call_s(fn_name, *args, **kws):
    rv = _server.call_s(fn_name, *_dumps([args, kws]))
    return _loads(*rv)


def callable(fn_or_name=None, require_user=None):
    if fn_or_name is None or isinstance(fn_or_name, str):
        _callable_decorator = _server.callable(fn_or_name, require_user=require_user)
        return lambda fn: _callable_decorator(
            _wrap_callable(_register(fn, fn_or_name, require_user))
        )

    return _server.callable(_wrap_callable(_register(fn_or_name)))


def call_async(fn_name, *args, **kws):
    from .. import non_blocking

    # non_blocking is client side only
    # we don't want this import to be top level if we're on the server

    return non_blocking.call_async(call_s, fn_name, *args, **kws)
