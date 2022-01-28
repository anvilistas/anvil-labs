# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from collections import namedtuple
from functools import partial

from anvil.server import portable_class

from .constants import CHANGE, DELETE, IS_SERVER_SIDE, REGISTRAR, SENTINEL
from .contexts import ActionContext
from .decorators import action
from .registrar import add_registrar
from .rendering import register, request
from .utils import MethodType, get_atom_prop_repr

__version__ = "0.0.1"


class BaseAction(
    namedtuple("_BaseAction", ["action", "atom", "prop", "value"], defaults=[None])
):
    """We use this as something we can pass to the action queue and might be consumed by a decorated subscriber"""

    def __str__(self):
        action, atom, prop, val = self
        val = f" = {val!r}" if action is CHANGE else ""
        return f"{action}: {get_atom_prop_repr(atom, prop)}{val}"


def as_atom(atom, prop, val):
    if type(val) is dict:
        return DictAtom(val)
    elif type(val) is list:
        return ListAtom(atom, prop, val)
    else:
        return val


_object_new = object.__new__


def atom(base):
    """decorator for an atom class"""
    if IS_SERVER_SIDE:
        return base

    class AtomProxy(base):
        """an AtomProxy requests an update whenever the __setattr__ is called
        and registers a relationship whenever __getattribute__ is called
        methods and dunder methods are ignored.
        """

        __slots__ = REGISTRAR  # slots don't actually work yet

        def __new__(cls, *args, **kws):
            base_new = base.__new__
            self = (
                _object_new(cls)
                if base_new is _object_new
                else base_new(cls, *args, **kws)
            )
            add_registrar(self)
            return self

        def __getattribute__(self, name: str):
            ret = base.__getattribute__(self, name)
            if not name.startswith("__") and type(ret) is not MethodType:
                # we ignore all dunder attributes and methods
                register(self, name)
            return ret

        def __setattr__(self, name, value):
            try:
                if base.__getattribute__(self, name) is value:
                    return
            except AttributeError:
                pass
            if name.startswith("__"):
                return base.__setattr__(self, name, value)
            value = as_atom(self, name, value)
            with ActionContext(BaseAction(CHANGE, self, name, value)):
                base.__setattr__(self, name, value)
                request(self, name)

        def __delattr__(self, name):
            if name.startswith("__"):
                base.__delattr__(self, name)
            with ActionContext(BaseAction(DELETE, self, name)):
                base.__delattr__(self, name)
                request(self, name)

        def __repr__(self):
            if base.__repr__ is object.__repr__:
                return f"<{base.__name__} atom>"
            else:
                return base.__repr__(self)

    AtomProxy.__name__ = base.__name__
    AtomProxy.__qualname__ = base.__qualname__
    AtomProxy.__module__ = base.__module__
    return AtomProxy


def portable_atom(_cls, name=None):
    """decorator to for atoms that you also want to be portable classes"""
    if IS_SERVER_SIDE:
        return portable_class(_cls, name)
    elif name is None and type(_cls) is str:
        name = _cls
        return lambda _cls: portable_atom(_cls, name)

    if not hasattr(_cls, "__serialize__"):
        # TODO remove this when skulpt has __slots__
        _cls.__serialize__ = lambda self, _: {
            k: v for k, v in self.__dict__.items() if k != REGISTRAR
        }
    return portable_class(atom(_cls), name)


KEYS = "dict.KEYS"
ITEMS = "dict.ITEMS"
VALUES = "dict.VALUES"


class DictAtom(dict):
    """
    a DictAtom requests an update whenever the __setitem__ is called
    and registers a relationship whenever __getitem__ is called
    """

    __slots__ = REGISTRAR

    def __init__(self, *args, **kws):
        target = dict(*args, **kws)
        dict.__init__(self, ((k, as_atom(self, k, v)) for k, v in target.items()))
        add_registrar(self)

    __hash__ = object.__hash__

    def __getitem__(self, key):
        register(self, key)
        res = dict.__getitem__(self, key)
        return res

    def __setitem__(self, key, val):
        current = dict.get(self, key, SENTINEL)
        if current is val:
            return
        val = as_atom(self, key, val)
        with ActionContext(BaseAction(CHANGE, self, key, val)):
            dict.__setitem__(self, key, val)
            request(self, key)
            request(self, VALUES)
            request(self, ITEMS)
            if val is SENTINEL:
                request(self, KEYS)

    def __delitem__(self, key):
        self.pop(key)

    @action
    def update(self, *args, **kws):
        for k, v in dict(*args, **kws).items():
            self[k] = v

    @action
    def clear(self):
        for k in dict.keys(self):
            self.pop(k)

    def pop(self, key, default=SENTINEL):
        if default is SENTINEL:
            res = dict.pop(self, key)
        else:
            res = dict.pop(self, key, SENTINEL)
            if res is SENTINEL:
                return default
        with ActionContext(BaseAction(DELETE, self, key)):
            request(self, key)
            request(self, VALUES)
            request(self, ITEMS)
            request(self, KEYS)
        return res

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def __iter__(self):
        # prevents dict(self) using the fast internal dict path
        # which makes it easier to depend on each atom in a list of DictAtoms
        # by calling [dict(atom) for dict_atom in list_atom]
        return dict.__iter__(self)

    def keys(self):
        register(self, KEYS)
        return dict.keys(self)

    def values(self):
        register(self, VALUES)
        return dict.values(self)

    def items(self):
        register(self, ITEMS)
        return dict.items(self)

    def __repr__(self):
        return f"DictAtom({dict.__repr__(self)})"


def _method(meth: str, convert_args=None):
    def fn(self, *args):
        if convert_args is not None:
            args = convert_args(self, *args)
        ret = getattr(list, meth)(self, *args)
        self._request_render()
        return ret

    fn.__name__ = meth
    fn.__qualname__ = "ListAtom." + meth
    return action(fn)


class ListAtom(list):
    """
    Any time the list is mutated we request a render from the parent atom at the property this list belongs to
    """

    slots = ["_as_atom", "_request_render", "_register"]

    def __init__(self, parent_atom, prop, target) -> None:
        list.__init__(self, (as_atom(parent_atom, prop, t) for t in target))
        self._as_atom = partial(as_atom, parent_atom, prop)
        self._request_render = partial(request, parent_atom, prop)
        self._register = partial(register, parent_atom, prop)

    def __getitem__(self, i):
        self._register()
        return list.__getitem__(self, i)

    __setitem__ = _method(
        "__setitem__",
        lambda self, i, val: [
            i,
            map(self._as_atom, val) if type(i) is slice else self._as_atom(val),
        ],
    )
    __delitem__ = _method("__delitem__")
    __iadd__ = _method("__iadd__", lambda self, x: [map(self._as_atom, x)])
    __imul__ = _method("__imul__")
    extend = _method("extend", lambda self, x: [map(self._as_atom, x)])
    remove = _method("remove")
    append = _method("append", lambda self, item: [self._as_atom(item)])
    insert = _method("insert", lambda self, i, item: [i, self._as_atom(item)])
    clear = _method("clear")
    pop = _method("pop")
    sort = _method("sort")
    reverse = _method("reverse")

    def __repr__(self):
        return f"ListAtom({list.__repr__(self)})"
