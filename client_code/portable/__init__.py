# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import json as _json
from functools import wraps as _wraps

import anvil.server as _server

from ._register import register
from ._serialize import UNHANDLED as _U
from ._serialize import reconstruct, serialize

__version__ = "0.0.1"


def _dumps(obj):
    s = serialize(obj)
    u = s.pop(_U)
    # we use repr for performance
    # anvil doesn't need to walk these objects
    return _json.dumps(s), u


def _loads(s, u):
    obj = _json.loads(s)
    obj[_U] = u
    return reconstruct(obj)


def call(fn_name, *args, **kws):
    rv = _server.call(fn_name, *_dumps([args, kws]))
    return _loads(*rv)


def callable(fn):
    @_wraps(fn)
    def wrapped(json_obj, unhandled):
        args, kws = _loads(json_obj, unhandled)
        rv = fn(*args, **kws)
        return _dumps(rv)

    return _server.callable(wrapped)
