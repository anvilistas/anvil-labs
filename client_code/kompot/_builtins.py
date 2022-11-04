# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import date, datetime
from math import isfinite

import anvil.tz
from anvil.server import portable_class

from ._register import get_registered_cls, register, registered_types

__version__ = "0.0.1"


class Builtin:
    @classmethod
    def __new_deserialized__(cls, data, info):
        return cls.__base__(data)


class Iterable(Builtin):
    def __serialize__(self, info):
        return list(self)


class Immutable(Builtin):
    def __serialize__(self, info):
        return str(self)


class Mapping(Builtin):
    def __serialize__(self, info):
        return [[k, v] for k, v in self.items()]


class Long(int, Immutable):
    def __new__(cls, x):
        if -2147483647 <= x <= 2147483647:
            return x
        return int.__new__(cls, x)


class Float(float, Immutable):
    def __new__(cls, x):
        if isfinite(x):
            return x
        return float.__new__(cls, x)


class Dict(dict, Mapping):
    pass


class Set(set, Iterable):
    pass


class FrozenSet(frozenset, Iterable):
    pass


class Tuple(tuple, Iterable):
    pass


class Bytes(bytes, Iterable):
    pass


class Date:
    def __init__(self, v: date):
        self.v = v

    def __serialize__(self, info):
        return self.v.isoformat()

    @staticmethod
    def __new_deserialized__(iso, info):
        return date.fromisoformat(iso)


class DateTime:
    def __init__(self, v: datetime):
        self.v = v

    def __serialize__(self, info):
        v = self.v
        if v.tzinfo is not None:
            offset = v.tzinfo.utcoffset(v).total_seconds()
        else:
            # Cannot import earlier - circular dependency!
            offset = anvil.tz.tzlocal().utcoffset(v).total_seconds()
        v = v.replace(tzinfo=anvil.tz.tzoffset(seconds=offset))
        return v.strftime("%Y-%m-%d %H:%M:%S.%f%z")

    @staticmethod
    def __new_deserialized__(iso, info):
        sign = iso[-5]
        has_offset = sign in ("+", "-")
        offset = 0
        if has_offset:
            hours = int(iso[-5:-2])
            mins = int(sign + iso[-2:])
            offset = hours * 60 + mins
            iso = iso[:-5]
        tzinfo = anvil.tz.tzoffset(minutes=offset)
        return datetime.fromisoformat(iso).replace(tzinfo=tzinfo)


class Type:
    def __init__(self, tp: type):
        try:
            self.name = registered_types[tp]
        except KeyError:
            raise ValueError(f"Cannot serialize an unregistered type, {tp.__name__}")

    def __serialize__(self, info):
        return self.name

    @staticmethod
    def __new_deserialized__(name, info):
        return get_registered_cls(name)


registered_builtins = {
    int: Long,
    float: Float,
    dict: Dict,
    set: Set,
    frozenset: FrozenSet,
    tuple: Tuple,
    date: Date,
    datetime: DateTime,
    type: Type,
    bytes: Bytes,
}


for cls in registered_builtins.values():
    portable_class(register(cls, name=cls.__name__))
