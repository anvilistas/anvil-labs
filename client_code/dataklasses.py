# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
#
# Original code: https://github.com/dabeaz/dataklasses
# Author: David Beazley (@dabeaz). http://www.dabeaz.com

from functools import lru_cache, reduce

from anvil.js.window import Function as _Function

__version__ = "0.0.1"

__all__ = ["dataklass"]


adjustRawPyFunction = _Function(
    "wrappedFunc",
    "fields",
    """
const clone = function(f) {
    const temp = function temporary() { return f.apply(this, arguments); };
    for (const key in f) {
        if (f.hasOwnProperty(key)) {
            temp[key] = f[key];
        }
    }
    return temp;
};

const func = Sk.ffi.toPy(wrappedFunc);
const func_code = func.func_code;
let co_varnames = func_code.co_varnames;
const start = co_varnames.indexOf("_0");
co_varnames = [...co_varnames.slice(0, start), ...fields, ...co_varnames.slice(start + fields.length)];
const copy = clone(func_code);
copy.co_varnames = co_varnames;
return new Sk.builtin.func(copy, func.func_globals);

""",
)


def codegen(func):
    @lru_cache
    def make_func_code(numfields):
        names = [f"_{n}" for n in range(numfields)]
        d = {}
        exec(func(names), {}, d)
        return d.popitem()[1]

    def decorate(fields):
        func = make_func_code(len(fields))
        return adjustRawPyFunction(func, list(fields))

    return decorate


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
    return (
        "def __repr__(self):\n"
        ' return f"{type(self).__name__}('
        + ", ".join("{self." + name + "!r}" for name in fields)
        + ')"\n'
    )


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
        f"   yield self.{name}" for name in fields
    )


@codegen
def make__hash__(fields):
    self_tuple = "(" + ",".join(f"self.{name}" for name in fields) + ",)"
    return "def __hash__(self):\n" f"    return hash({self_tuple})\n"


def dataklass(cls):
    fields = all_hints(cls)
    clsdict = cls.__dict__
    print(fields)
    print(clsdict)
    if "__init__" not in clsdict:
        cls.__init__ = make__init__(fields)
    if "__repr__" not in clsdict:
        cls.__repr__ = make__repr__(fields)
    if "__eq__" not in clsdict:
        cls.__eq__ = make__eq__(fields)
    if "__iter__" not in clsdict:
        cls.__iter__ = make__iter__(fields)
    if "__hash__" not in clsdict:
        cls.__hash__ = make__hash__(fields)
    cls.__match_args__ = fields
    return cls


# Example use
if __name__ == "__main__":

    @dataklass
    class Coordinates:
        x: int
        y: int

    print(Coordinates(1, 3))
