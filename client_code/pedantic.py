# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


class BaseValidator:
    value = None

    def is_valid(self):
        raise NotImplementedError

    def __get__(self, obj):
        return self.value

    def __set__(self, obj, value):
        self.value = value
        if not self.is_valid():
            raise ValueError(f"{value} is not a valid value")


def add_validator(cls, attr, validator):
    cls.validators.append(validator.is_valid)
    setattr(cls, attr, validator)


def _is_valid(obj):
    return all(v() for v in obj.validators)


def validated(cls):
    setattr(cls, "validators", [])
    setattr(cls, "is_valid", _is_valid)
    return cls


class InList(BaseValidator):
    """A class to validate that an attribute value is in a list of permitted values."""

    def __init__(self, items):
        self.items = items

    def is_valid(self):
        return self.value in self.items


def in_list(attr, items):
    """A function to add an @in_list decorator to a class"""

    def decorator(cls):
        add_validator(cls, attr, InList(items))
        return cls

    return decorator
