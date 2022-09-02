# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
#
# Original code: https://github.com/dabeaz/dataklasses
# Author: David Beazley (@dabeaz). http://www.dabeaz.com

from functools import lru_cache, reduce

import anvil.server
from anvil import is_server_side

__version__ = "0.0.1"

__all__ = ["dataklass", "portable_dataklass"]

if is_server_side():

    def codegen(func):
        @lru_cache(maxsize=128)
        def make_func_code(numfields):
            names = [f"_{n}" for n in range(numfields)]
            d = {}
            exec(func(names), {}, d)
            return d.popitem()[1]

        return make_func_code

    def patch_args_and_attributes(func, fields, start=0):
        return type(func)(
            func.__code__.replace(
                co_names=(*func.__code__.co_names[:start], *fields),
                co_varnames=("self", *fields),
            ),
            func.__globals__,
        )

    def patch_attributes(func, fields, start=0):
        return type(func)(
            func.__code__.replace(co_names=(*func.__code__.co_names[:start], *fields)),
            func.__globals__,
        )

    def get_nfields(fields):
        return len(fields)

else:
    # We can't do any clever caching so don't bother
    def codegen(func):
        def make_func_code(fields):
            d = {}
            exec(func(fields), {}, d)
            return d.popitem()[1]

        return make_func_code

    def patch_args_and_attributes(func, fields, start=0):
        return func

    def patch_attributes(func, fields, start=0):
        return func

    def get_nfields(fields):
        return fields


def all_hints(cls):
    return reduce(
        lambda x, y: x | getattr(y, "__annotations__", {}), reversed(cls.__mro__), {}
    )


@codegen
def make__init__(fields):
    code = "def __init__(self, " + ",".join(fields) + "):\n"
    return code + "\n".join(f" self.{name} = {name}\n" for name in fields)


@codegen
def make__repr__(fields):
    args = ", ".join(
        "{self.__match_args__[" + str(i) + "]}={self." + name + "!r}"
        for i, name in enumerate(fields)
    )
    return "def __repr__(self):\n" ' return f"{type(self).__name__}(' + args + ')"\n'


@codegen
def make__eq__(fields):
    selfvals = ",".join(f"self.{name}" for name in fields)
    othervals = ",".join(f"other.{name}" for name in fields)
    return (
        "def __eq__(self, other):\n"
        "  if self.__class__ is other.__class__:\n"
        f"    return ({selfvals},) == ({othervals},)\n"
        "  else:\n"
        "    return NotImplemented\n"
    )


@codegen
def make__iter__(fields):
    return "def __iter__(self):\n" + "\n".join(
        f"  yield self.{name}" for name in fields
    )


@codegen
def make__hash__(fields):
    self_tuple = "(" + ",".join(f"self.{name}" for name in fields) + ",)"
    return "def __hash__(self):\n" f"  return hash({self_tuple})\n"


def dataklass(cls):
    fields = all_hints(cls)
    nfields = get_nfields(fields)
    clsdict = cls.__dict__
    if "__init__" not in clsdict:
        cls.__init__ = patch_args_and_attributes(make__init__(nfields), fields)
    if "__repr__" not in clsdict:
        cls.__repr__ = patch_attributes(make__repr__(nfields), fields, 3)
    if "__eq__" not in clsdict:
        cls.__eq__ = patch_attributes(make__eq__(nfields), fields, 1)
    if "__iter__" not in clsdict:
        cls.__iter__ = patch_attributes(make__iter__(nfields), fields)
    if "__hash__" not in clsdict:
        cls.__hash__ = patch_attributes(make__hash__(nfields), fields, 1)
    cls.__match_args__ = tuple(fields)
    return cls


def portable_dataklass(cls):
    return anvil.server.portable_class(dataklass(cls))


# Example use
if __name__ == "__main__":

    @dataklass
    class Coordinates:
        x: int
        y: int

    print(Coordinates(1, 3).x)
    print(Coordinates(1, 3))
