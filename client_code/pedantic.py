# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


class BaseValidator:

    def is_valid(self):
        raise NotImplementedError

    def __get__(self, obj, owner):
        return self.value

    def __set__(self, obj, value):
        self.value = value
        if not self.is_valid():
            raise ValueError(f"{value} is not a valid value")


def _is_valid(obj):
    return all(v() for v in obj.validators)


def validate(**kwargs):
    def decorator(cls):
        try:
            _ = cls.validators
        except AttributeError:
            cls.validators = []

        try:
            _ = cls.is_valid
        except AttributeError:
            cls.is_valid = _is_valid

        for attr, validator in kwargs.items():
            if getattr(cls, attr, None) is not None:
                raise ValueError(f"{attr} is already defined")
            setattr(cls, attr, validator)
            cls.validators.append(validator.is_valid)
        return cls

    return decorator


class InList(BaseValidator):
    """A class to validate that an attribute value is in a list of permitted values."""

    def __init__(self, items):
        self.items = items

    def is_valid(self):
        return self.value in self.items
