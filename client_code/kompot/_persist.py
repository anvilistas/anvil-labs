# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

"""A module to provide persistence mechanisms for a class.

e.g.

For a class named 'Book', we might have a data table named 'book' where each row
corresponds to instance of the Book class. We might also have server functions to
add new row or to update existing entries:

@row_backed_class
class Book:
    server_functions = {
        "create": "add_book",
        "get": "get_book",
        "update": "update_book",
        "delete": "delete_book",
    }

Create a new Book instance and fetch its row from the db:

book = Book()
book.get(title="Fluent Python")

This assumes a server function exists named 'get_book', which take a title argument
and returns a data tables row.

All the columns from the row will now be available as attributes on the Book instance.
e.g.

print(book.title)
>>> Fluent Python
"""

import anvil.server

from ._register import register

__version__ = "0.0.1"


@register
@anvil.server.portable_class
class Despatcher:
    """A portable class for sending payloads from client to server

    When changes are made to a persisted object, a Despatcher instance records those
    changes so they can be sent to the server if required.

    This is particularly useful for classes backed by data tables rows since a row
    cannot be created or updated on the client.
    """

    def __init__(self):
        self._changed_attrs = set()

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._changed_attrs.add(name)
            object.__setattr__(self, name, value)

    @property
    def synced(self):
        """Whether there are any pending changes recorded."""
        return not self._changed_attrs

    def clear(self):
        """Clear any pending changes."""
        for attr in self._changed_attrs:
            delattr(self, attr)
        self._changed_attrs = set()


class LinkedAttribute:
    """A descriptor class for adding linked table items as attributes

    For a class backed by a data tables row, this class is used to dyamically add
    linked table items as attributes to the parent object.
    """

    def __init__(self, name, linked_table, linked_attr):
        """
        Parameters
        ----------
        name: str
            The name which should be used for the dynamic attribute which is added
        linked_table: str
            The name of the column in the row object which links to another table
        linked_attr: str
            The name of the column in the linked table which contains the required
            value
        """
        self._name = name
        self._linked_table = linked_table
        self._linked_attr = linked_attr

    def __get__(self, instance, objtype=None):
        if instance is None:
            raise AttributeError(f"{objtype.__name__} class has no such attribute")

        if instance._row and instance._despatcher.synced:
            return instance._row[self._linked_table][self._linked_attr]
        else:
            return getattr(instance._despatcher, self._linked_attr, None)

    def __set__(self, instance, value):
        instance._set_value(self._name, value)


class RowBackedStore:
    """A class to hold a data tables row as the persistence mechanism for an object"""

    def __init__(self, server_functions, linked_attributes, row=None, despatcher=None):
        """
        Parameters
        ----------
        server_functions: dict
            mapping the keys 'create', 'get', 'update' and 'delete' to the name of the
            relevant server function for that action
        linked_attributes: dict
            mapping the name of a linked column to a further dict which then maps the
            required name for the dynamically created attribute to the name of the
            relevant column in the linked table
        row: anvil.tables.Row
        despatcher: any
            A portable class suitable for sending changes from client to server
        """
        self._initialised = False
        self._row = row
        self._despatcher = despatcher or Despatcher()
        self._server_functions = server_functions
        for linked_table, attributes in linked_attributes.items():
            for attr, linked_attr in attributes.items():
                setattr(
                    self.__class__,
                    attr,
                    LinkedAttribute(attr, linked_table, linked_attr),
                )
        self._initialised = True

    def __getattr__(self, name):
        if self._row and self._despatcher.synced:
            return self._row[name]
        else:
            return getattr(self._despatcher, name, None)

    def __setattr__(self, name, value):
        if name.startswith("_") or not self._initialised:
            object.__setattr__(self, name, value)
        else:
            setattr(self._despatcher, name, value)

    def _despatch(self, action):
        result = kompot.call(
            self._server_functions[action], self.despatcher.serialize()
        )
        self.despatcher.clear()
        return result

    def get(self, *args, **kwargs):
        "Fetch a data tables row and make it available to the parent object"
        self._row = anvil.server.call(self._server_functions["get"], *args, **kwargs)
        self._despatcher.clear()

    def create(self):
        """Create a new data tables row from the parent object"""
        return self._despatch("create")

    def save(self):
        """Save changes made to the parent object to the data tables row"""
        action = "update" if self._row else "create"
        return self._despatch(action)

    def delete(self):
        """Delete the data tables row"""
        return self._despatch("delete")


def _get_value(self, key):
    if not key.startswith("_"):
        try:
            return getattr(self._store, key)
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__} instance has no store defined"
            )


def _set_value(self, key, value):
    if key.startswith("_"):
        object.__setattr__(self, key, value)
    else:
        try:
            setattr(self._store, key, value)
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__} instance has no store defined"
            )


def _get(self, *args, **kwargs):
    return self._store.get(*args, **kwargs)


def _create(self):
    return self._store.create()


def _save(self):
    return self._store.save()


def _delete(self):
    return self._store.delete()


def persisted_class(cls):
    """A decorator for a class with a persistence mechanism"""
    members = {
        "__module__": cls.__module__,
        "__getattr__": _get_value,
        "__getitem__": _get_value,
        "__setattr__": _set_value,
        "__setitem__": _set_value,
        "get": _get,
        "create": _create,
        "save": _save,
        "delete": _delete,
    }
    class_members = {k: v for k, v in cls.__dict__.items() if k not in members}
    members.update(class_members)
    return type(cls.__name__, (object,), members)


def _row_backed_constructor(self):
    def init(self, row=None):
        self.store = RowBackedStore(self.server_functions, self.linked_attributes, row)

    return init


def row_backed_class(cls):
    """A decorator for a class persisted by a data tables row"""
    _cls = persisted_class(cls)
    setattr(_cls, "__init__", _row_backed_constructor)
    return _cls
