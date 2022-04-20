# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import json as _json
from functools import wraps as _wraps

import anvil.server as _server

from ._register import register
from ._serialize import UNHANDLED as _U
from ._serialize import reconstruct, serialize

__version__ = "0.0.1"


def to_json(obj):
    rv = serialize(obj)
    unhandled = rv.pop(_U)
    if unhandled:
        raise _server.SerializationError(
            f"Unable to serialize the following: {', '.join(repr(x) for x in unhandled)}"
        )
    return _json.dumps(rv)


def from_json(json_obj):
    return reconstruct(_json.loads(json_obj))


def call(fn_name, *args, **kws):
    return reconstruct(_server.call(fn_name, serialize([args, kws])))


def callable(fn):
    @_wraps(fn)
    def wrapped(obj):
        args, kws = reconstruct(obj)
        return serialize(fn(*args, **kws))

    return _server.callable(wrapped)
