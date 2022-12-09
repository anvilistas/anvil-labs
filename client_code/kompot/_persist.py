# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

"""A module to provide persistence mechanisms for a class.

e.g.

For a class named 'Book', we might have a data table named 'book' where each row
corresponds to instance of the Book class. We might also have server functions to
add a new row or to update existing entries:

@row_backed_class
class Book:
    pass

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
from ._rpc import call
from ._serialize import serialize

__version__ = "0.0.1"


@register
@anvil.server.portable_class
class Dispatcher:
    """A portable class for sending payloads from client to server

    When changes are made to a persisted object, a Dispatcher instance records those
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

        store = instance._store
        dispatcher = store._dispatcher
        if not dispatcher.synced:
            try:
                return getattr(dispatcher, self._name)
            except AttributeError:
                return store._row[self._linked_column][self._linked_attr]
        else:
            return store._row[self._linked_column][self._linked_attr]

    def __set__(self, instance, value):
        setattr(instance._store._dispatcher, self._name, value)


class ServerFunction:
    def __init__(self, name, with_kompot=False):
        self.name = name
        self.with_kompot = with_kompot

    def __call__(self, *args, **kwargs):
        caller = call if self.with_kompot else anvil.server.call
        return caller(self.name, *args, **kwargs)


class RowBackedStore:
    """A class to hold a data tables row as the persistence mechanism for an object"""

    def __init__(self, server_functions, row=None, dispatcher=None):
        """
        Parameters
        ----------
        server_functions: dict
            mapping the keys 'creator', 'getter', 'updater' and 'deleter' to the name
            of the relevant server function for that action
        row: anvil.tables.Row
        dispatcher: any
            A portable class suitable for sending changes from client to server
        """
        self._initialised = False
        self._row = row
        self._dispatcher = dispatcher or Dispatcher()
        self._server_functions = server_functions
        self._initialised = True

    def __getattr__(self, name):
        if not self._dispatcher.synced:
            try:
                return getattr(self._dispatcher, name)
            except AttributeError:
                return self._row[name]
        else:
            return self._row[name]

    def __setattr__(self, name, value):
        if name.startswith("_") or not self._initialised:
            object.__setattr__(self, name, value)
        else:
            setattr(self._dispatcher, name, value)

    def get(self, *args, **kwargs):
        "Fetch a data tables row and make it available to the parent object"
        self._row = self._server_functions["getter"](*args, **kwargs)
        self._dispatcher.clear()

    def create(self):
        """Create a new data tables row from the parent object"""
        result = self._server_functions["creator"](changes=serialize(self._dispatcher))
        self._dispatcher.clear()
        return result

    def update(self):
        """Save changes made to the parent object to the data tables row"""
        result = self._server_functions["updater"](
            changes=serialize(self._dispatcher), row=self._row
        )
        self._dispatcher.clear()
        return result

    def delete(self):
        """Delete the data tables row"""
        result = self._server_functions["deleter"](row=self._row)
        self._dispatcher.clear()
        return result

    def reset(self):
        self._dispatcher.clear()


def _get_value(self, key):
    if not key.startswith("_"):
        try:
            return getattr(self._store, key)
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__} instance has no store defined"
            )


def _set_value(self, key, value):
    is_private = key.startswith("_")
    is_linked_attribute = hasattr(self.__class__, key) and isinstance(
        getattr(self.__class__, key), LinkedAttribute
    )
    if is_private or is_linked_attribute:
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


def _reset(self):
    self._store.reset()


MEMBERS = {
    "__getattr__": _get_value,
    "__getitem__": _get_value,
    "__setattr__": _set_value,
    "__setitem__": _set_value,
    "get": _get,
    "create": _create,
    "save": _save,
    "delete": _delete,
    "reset": _reset,
}


def persisted_class(cls):
    """A decorator for a class with a persistence mechanism"""
    return type(cls.__name__, (object,), dict(cls.__dict__, **MEMBERS))


def _combine_server_functions(cls):
    class_name = cls.__name__.lower()
    defaults = {
        "getter": ServerFunction(name=f"get_{class_name}"),
        "creator": ServerFunction(name=f"create_{class_name}", with_kompot=True),
        "updater": ServerFunction(name=f"update_{class_name}", with_kompot=True),
        "deleter": ServerFunction(name=f"delete_{class_name}"),
    }
    members = {k: v for k, v in cls.__dict__.items() if isinstance(v, ServerFunction)}
    return dict(defaults, **members)


def _row_backed_init(self, row=None):
    self._store = RowBackedStore(self._server_functions, row)


def row_backed_class(cls):
    """A decorator for a class persisted by a data tables row"""
    _cls = persisted_class(cls)
    setattr(_cls, "_server_functions", _combine_server_functions())
    setattr(_cls, "__init__", _row_backed_init)
    return _cls
