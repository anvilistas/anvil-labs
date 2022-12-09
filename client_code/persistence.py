# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
# import anvil.server
import anvil.server

__version__ = "0.0.1"


class LinkedAttribute:
    """A descriptor class for adding linked table items as attributes

    For a class backed by a data tables row, this class is used to dyamically add
    linked table items as attributes to the parent object.
    """

    def __init__(self, linked_column, linked_attr):
        """
        Parameters
        ----------
        linked_column: str
            The name of the column in the row object which links to another table
        linked_attr: str
            The name of the column in the linked table which contains the required
            value
        """
        self._linked_column = linked_column
        self._linked_attr = linked_attr

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, objtype=None):
        if instance is None:
            return self

        if instance._delta:
            return instance._delta[self._name]

        return instance._store[self._linked_column][self._linked_attr]

    def __set__(self, instance, value):
        instance._delta[self._name] = value


class ServerFunction:
    def __init__(self, target, caller=None):
        self.target = target
        self.caller = caller or anvil.server.call

    def __call__(self, *args, **kwargs):
        return self.caller(self.target, *args, **kwargs)


@classmethod
def _create(cls, store=None, delta=None, *args, **kwargs):
    instance = cls(*args, **kwargs)
    instance._store = store or {}
    instance._delta = delta or {}
    return instance


def _get_value(self, key):
    if self._delta and key in self._delta:
        return self._delta[key]

    return self._store[key]


def _set_value(self, key, value):
    is_private = key.startswith("_")
    is_linked_attribute = hasattr(self.__class__, key) and isinstance(
        getattr(self.__class__, key), LinkedAttribute
    )
    if is_private or is_linked_attribute:
        object.__setattr__(self, key, value)
    else:
        self._delta[key] = value


MEMBERS = {
    "create": _create,
    "__getattr__": _get_value,
    "__getitem__": _get_value,
    "__setattr__": _set_value,
    "__setitem__": _set_value,
}


def _members(cls):
    class_name = cls.__name__.lower()
    keys = ["get", "save", "delete"]
    default_server_functions = {
        key: ServerFunction(target=f"{key}_{class_name}")
        for key in keys
        if key not in cls.__dict__
    }
    user_defined_server_functions = {
        k: v for k, v in cls.__dict__.items() if isinstance(v, ServerFunction)
    }
    return dict(MEMBERS, **default_server_functions, **user_defined_server_functions)


def persisted_class(cls):
    """A decorator for a class with a persistence mechanism"""
    return type(cls.__name__, (object,), dict(cls.__dict__, **_members(cls)))
