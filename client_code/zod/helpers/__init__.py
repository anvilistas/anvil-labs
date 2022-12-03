# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from datetime import date, datetime

from ...cluegen import DatumBase, cluegen
from .parse_util import MISSING
from .util import enum

__version__ = "0.0.1"


def all_slots(cls):
    slots = []
    for cls in cls.__mro__:
        slots[0:0] = getattr(cls, "__slots__", [])
    return slots


class Slotum(DatumBase):
    __slots__ = ()

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.__match_args__ = tuple(all_slots(cls))

    @cluegen
    def __init__(cls):
        slots = all_slots(cls)
        return (
            "def __init__(self, "
            + ",".join(slots)
            + "):\n"
            + "\n".join(f"    self.{name} = {name}" for name in slots)
        )

    @cluegen
    def __repr__(cls):
        slots = all_slots(cls)
        return (
            "def __repr__(self):\n"
            + f'    return f"{cls.__name__}('
            + ", ".join("%s={self.%s!r}" % (name, name) for name in slots)
            + ')"'
        )

    @cluegen
    def keys(cls):
        slots = all_slots(cls)
        return "def keys(self):\n" + f"  return {slots!r}"

    @cluegen
    def __getitem__(cls):
        slots = all_slots(cls)
        return (
            "def __getitem__(self, key):\n"
            + f"  if key in {slots!r}:\n"
            + "    return getattr(self, key)\n"
            + "  raise KeyError(key)"
        )


# Adjusted for python
ZodParsedType = enum(
    "ZodParsedType",
    [
        "string",
        # "nan",
        "number",
        "integer",
        "float",
        "boolean",
        "date",
        # "bigint",
        # "symbol",
        "function",
        # "undefined",
        "missing",
        "none",  # skulpt doesn't like null
        "array",
        "tuple",
        # "object",
        "mapping",
        "unknown",
        # "promise",
        # "void",
        "never",
        "map",
        "set",
    ],
)

FuncType = type(lambda: None)
NoneType = type(None)


def get_parsed_type(data):
    if data is MISSING:
        return ZodParsedType.missing

    t = type(data)

    if t is NoneType:
        return ZodParsedType.none

    if t is str:
        return ZodParsedType.string
    if t is bool:
        return ZodParsedType.boolean

    if t is int:
        return ZodParsedType.integer

    if t is float:
        return ZodParsedType.float

    if t is list:
        return ZodParsedType.array

    if t is tuple:
        return ZodParsedType.tuple

    if t is set:
        return ZodParsedType.set

    if t is date:
        return ZodParsedType.date

    if t is datetime:
        return ZodParsedType.datetime

    if t is dict:
        return ZodParsedType.mapping

    if hasattr(t, "keys") and hasattr(t, "__getitem__"):
        return ZodParsedType.mapping

    return ZodParsedType.unknown
