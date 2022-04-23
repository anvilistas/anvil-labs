# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from anvil.server import SerializationError

from ._builtins import registered_builtins
from ._register import get_registered_cls, registered_types

__version__ = "0.0.1"

VALUE = "_"
PATHS = "P"
TYPES = "T"
UNHANDLED = "X"


def serialize_portable_class(obj, cls, path, paths, types, unhandled):
    __serialize__ = getattr(obj, "__serialize__", None)
    if __serialize__ is not None:
        data = __serialize__(None)
        rv = do_remap(data, path, paths, types, unhandled)
    else:
        # `do_remap(obj.__dict__, ....)` also works here
        # which would give us a list of items - see Dict.__serialize__
        # but since we don't care about this dict being ordered, and we know the keys are strings
        # we can serialize it directly as a JSON object
        rv = {}
        for k, v in obj.__dict__.items():
            path.append(k)
            rv[k] = do_remap(v, path, paths, types, unhandled)
            path.pop()

    paths.append(path[:])
    types.append(registered_types[cls])
    return rv


def serialize_builtin(obj, builtin, path, paths, types, unhandled):
    cls = registered_builtins[builtin]
    obj = cls(obj)
    if type(obj) is builtin:
        # floats and ints use this
        return obj
    return serialize_portable_class(obj, cls, path, paths, types, unhandled)


NoneType = type(None)


def do_remap(obj, path, paths, types, unhandled):
    tp = type(obj)

    if tp in (NoneType, str, bool):
        return obj

    if tp is list:
        rv = []
        for i, o in enumerate(obj):
            path.append(i)
            rv.append(do_remap(o, path, paths, types, unhandled))
            path.pop()
        return rv

    if tp in registered_builtins:
        return serialize_builtin(obj, tp, path, paths, types, unhandled)

    if tp in registered_types:
        return serialize_portable_class(obj, tp, path, paths, types, unhandled)

    # we don't know how to serialize - it could be a table row, media object, capability
    # leave it alone and let anvil handle it
    types.append(None)
    paths.append(path[:])
    unhandled.append(obj)
    return None


def serialize(obj):
    types = []
    unhandled = []
    paths = []
    val = do_remap(obj, [VALUE], paths, types, unhandled)
    return {VALUE: val, PATHS: paths, TYPES: types, UNHANDLED: unhandled}


def reconstruct_portable_class(tp_name: str, data):
    cls = get_registered_cls(tp_name)
    new_deserialized = getattr(cls, "__new_deserialized__", None)
    if new_deserialized is not None:
        return new_deserialized(data, None)

    obj = cls.__new__(cls)
    deserialize = getattr(obj, "__deserialize__", None)
    if deserialize is not None:
        deserialize(data, None)
    else:
        obj.__dict__.update(data)

    return obj


def reconstruct(json_obj):
    paths, types = json_obj[PATHS], json_obj[TYPES]
    unhandled = iter(json_obj.get(UNHANDLED, []))

    for path, tp in zip(paths, types):
        is_portable = tp is not None

        if not is_portable:
            tp = next(unhandled)

        data = json_obj
        for key in path:
            prev, data = data, data[key]

        if is_portable:
            prev[key] = reconstruct_portable_class(tp, data)
        else:
            prev[key] = tp

    return json_obj[VALUE]


def preserve(obj):
    rv = serialize(obj)
    unhandled = rv.pop(UNHANDLED)

    if unhandled:
        msg = f"Unable to serialize the following object(s): {', '.join(map(repr, unhandled))}"
        raise SerializationError(msg)

    return rv
