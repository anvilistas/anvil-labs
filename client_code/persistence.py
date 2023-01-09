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
        if name == self._linked_column:
            raise ValueError(
                "Attribute name cannot be the same as the linked column name"
            )
        self._name = name

    def __get__(self, instance, objtype=None):
        if instance is None:
            return self

        if instance._delta:
            return instance._delta[self._name]

        if not instance._store:
            return None

        return instance._store[self._linked_column][self._linked_attr]

    def __set__(self, instance, value):
        instance._delta[self._name] = value


class LinkedClass:
    "A descriptor class for adding objects based on linked tables as attributes"

    def __init__(self, linked_column, constructor, *args, **kwargs):
        self._linked_column = linked_column
        self._constructor = constructor
        self._obj = None
        self._args = args or []
        self._kwargs = kwargs or {}

    def __get__(self, instance, objtype=None):
        if instance is None:
            return self

        if self._obj is None:
            self._obj = self._constructor(
                instance._store[self._linked_column], *self._args, **self._kwargs
            )

        return self._obj

    def __set__(self, instance, value):
        raise ValueError("Linked Class instance is already set and cannot be changed")


@classmethod
def _search(cls, *args, **kwargs):
    rows = anvil.server.call(f"search_{cls.__name__.lower()}", *args, **kwargs)
    return (cls.create(store=row) for row in rows)


@classmethod
def _create(cls, store=None, delta=None, *args, **kwargs):
    instance = cls(*args, **kwargs)
    instance._store = store or {}
    instance._delta = delta or {}
    return instance


def _getattr(self, key):
    if self._delta and key in self._delta:
        return self._delta[key]

    return dict(self._store).get(key, None)


def _getitem(self, key):
    return getattr(self, key)


def _set_value(self, key, value):
    is_private = key.startswith("_")
    is_descriptor = hasattr(self.__class__, key) and hasattr(
        getattr(self.__class__, key), "__set__"
    )
    if is_private or is_descriptor:
        object.__setattr__(self, key, value)
    else:
        self._delta[key] = value


def _class_name(instance):
    return "".join(
        "_" + c.lower() if c.isupper() else c for c in instance.__class__.__name__
    ).lstrip("_")


def _get(self, *args, **kwargs):
    self._store = anvil.server.call(f"get_{_class_name(self)}", *args, **kwargs)
    self._delta.clear()


def _add(self, *args, **kwargs):
    self._store = anvil.server.call(
        f"add_{_class_name(self)}", self._delta, *args, **kwargs
    )
    self._delta.clear()


def _update(self, *args, **kwargs):
    anvil.server.call(
        f"update_{_class_name(self)}", self._store, self._delta, *args, **kwargs
    )
    self._delta.clear()


def _delete(self, *args, **kwargs):
    anvil.server.call(f"delete_{_class_name(self)}", self._store, *args, **kwargs)
    self._delta.clear()


MEMBERS = {
    "search": _search,
    "create": _create,
    "__getattr__": _getattr,
    "__getitem__": _getitem,
    "__setattr__": _set_value,
    "__setitem__": _set_value,
    "get": _get,
    "add": _add,
    "update": _update,
    "delete": _delete,
}


def persisted_class(cls):
    """A decorator for a class with a persistence mechanism"""
    return type(cls.__name__, (object,), dict(MEMBERS, **cls.__dict__))
