# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from ._builtins import registered_builtins
from ._register import get_registered_cls, registered_types

__version__ = "0.0.1"

VALUE = "_"
OBJECTS = "O"
UNHANDLED = "X"


def serialize_portable_class(obj, cls, path, non_json, unhandled):
    __serialize__ = getattr(obj, "__serialize__", None)
    if __serialize__ is not None:
        data = __serialize__(None)
        rv = do_remap(data, path, non_json, unhandled)
    else:
        # we don't need to sort this dict
        rv = {}
        for k, v in obj.__dict__.items():
            path.append(k)
            rv[k] = do_remap(v, path, non_json, unhandled)
            path.pop()

    non_json.append([registered_types[cls], path[:]])
    return rv


def serialize_builtin(obj, builtin, path, non_json, unhandled):
    cls = registered_builtins[builtin]
    obj = cls(obj)
    if type(obj) is builtin:
        return obj
    return serialize_portable_class(obj, cls, path, non_json, unhandled)


NoneType = type(None)


def do_remap(obj, path, non_json, unhandled):
    tp = type(obj)

    if tp in (NoneType, str, bool):
        return obj
    elif tp is list:
        rv = []
        for i, o in enumerate(obj):
            path.append(i)
            rv.append(do_remap(o, path, non_json, unhandled))
            path.pop()
        return rv
    elif tp in registered_builtins:
        return serialize_builtin(obj, tp, path, non_json, unhandled)
    elif tp in registered_types:
        return serialize_portable_class(obj, tp, path, non_json, unhandled)

    non_json.append(None)
    unhandled.append([obj, path[:]])
    return None


def serialize(obj):
    non_json = []
    unhandled = []
    val = do_remap(obj, [VALUE], non_json, unhandled)
    return {VALUE: val, OBJECTS: non_json, UNHANDLED: unhandled}


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
    objects = json_obj[OBJECTS]
    unhandled = iter(json_obj.get(UNHANDLED, []))
    for obj in objects:
        is_portable = obj is not None

        if not is_portable:
            obj = next(unhandled)

        val, path = obj
        data = json_obj
        for key in path:
            prev, data = data, data[key]

        if is_portable:
            prev[key] = reconstruct_portable_class(val, data)
        else:
            prev[key] = val

    return json_obj[VALUE]
