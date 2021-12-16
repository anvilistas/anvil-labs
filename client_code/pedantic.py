# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


class InList:
    """A class to validate that an attribute value is in a list of permitted values."""

    def __init__(self, items):
        self.items = items

    def __get__(self, obj):
        return self.value

    def __set__(self, obj, value):
        if value not in self.items:
            raise ValueError(f"{value} is not a valid value")
        self.value = value


def in_list(attr, items):
    """A function to add an @in_list decorator to a class"""

    def decorator(cls):
        setattr(cls, attr, InList(items))
        return cls

    return decorator
