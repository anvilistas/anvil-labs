# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from anvil.server import SerializationError

from anvil_extras.utils import import_module

__version__ = "0.0.1"

registered_types = {}
registered_names = {}


def register(cls, name=None):
    if name is None:
        name = cls.__module__ + "." + cls.__name__
    registered_types[cls] = name
    registered_names[name] = cls
    return cls


def get_registered_cls(tp_name):
    try:
        return registered_names[tp_name]
    except KeyError:
        pass

    # assume we've sent a portable_class across the wire
    # if we're now on the server then the client module might need to be imported
    # we do that now and try to get the registered cls after the import
    mod, _ = tp_name.rsplit(".", 1)
    import_module(mod)
    try:
        return registered_names[tp_name]
    except KeyError:
        raise SerializationError(f"Unregistered type {tp_name}")
