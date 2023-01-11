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

    def __init__(self, cls, linked_column=None, *args, **kwargs):
        self._linked_column = linked_column
        self._cls = cls
        self._obj = None
        self._args = args or []
        self._kwargs = kwargs or {}

    def __set_name__(self, owner, name):
        if self._linked_column is None:
            self._linked_column = name

    def __get__(self, instance, objtype=None):
        if instance is None:
            return self

        if self._obj is None:
            self._obj = self._cls(
                instance._store[self._linked_column], *self._args, **self._kwargs
            )

        return self._obj

    def __set__(self, instance, value):
        raise AttributeError(
            "Linked Class instance is already set and cannot be changed"
        )


class PersistedClass:
    @classmethod
    def search(cls, *args, **kwargs):
        rows = anvil.server.call(f"search_{cls.__name__.lower()}", *args, **kwargs)
        return (cls.create(store=row) for row in rows)

    def __init__(self, store=None, delta=None, *args, **kwargs):
        self._store = store or {}
        self._delta = delta or {}

    def __getattr__(self, key):
        if self._delta and key in self._delta:
            return self._delta[key]

        return dict(self._store).get(key, None)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setattr__(self, key, value):
        is_private = key.startswith("_")
        is_descriptor = hasattr(self.__class__, key) and hasattr(
            getattr(self.__class__, key), "__set__"
        )
        if is_private or is_descriptor:
            object.__setattr__(self, key, value)
        else:
            self._delta[key] = value

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def _class_name(self):
        return "".join(
            "_" + c.lower() if c.isupper() else c for c in self.__class__.__name__
        ).lstrip("_")

    def get(self, *args, **kwargs):
        self._store = anvil.server.call(f"get_{self._class_name()}", *args, **kwargs)
        self._delta.clear()

    def add(self, *args, **kwargs):
        self._store = anvil.server.call(
            f"add_{self._class_name()}", self._delta, *args, **kwargs
        )
        self._delta.clear()

    def update(self, *args, **kwargs):
        anvil.server.call(
            f"update_{self._class_name()}", self._store, self._delta, *args, **kwargs
        )
        self._delta.clear()

    def delete(self, *args, **kwargs):
        anvil.server.call(f"delete_{self._class_name()}", self._store, *args, **kwargs)
        self._delta.clear()


def persisted_class(cls):
    """A decorator for a class with a persistence mechanism"""
    user_members = cls.__dict__.copy()
    for attr, value in user_members.items():
        try:
            is_persisted_class = issubclass(value, PersistedClass)
        except TypeError:
            is_persisted_class = False

        if is_persisted_class:
            user_members[attr] = LinkedClass(cls=value)

    return type(cls.__name__, (PersistedClass,), user_members)
