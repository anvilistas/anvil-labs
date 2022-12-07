# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from datetime import date, datetime

from .parse_util import MISSING
from .util import enum

__version__ = "0.0.1"


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
        "datetime",
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
