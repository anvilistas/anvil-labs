# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from anvil.server import AnvilWrappedError, _register_exception_type

__version__ = "0.0.1"

class NamedError(AnvilWrappedError):
    """A base class for custom error classes

    In order to register a custom error class, a name is required. This base class
    ensures that a 'name' class attribute exists with a default value for use by
    portable_exception.

    It can be overridden in any subclass that requires a customised name.
    """

    name = None


def portable_exception(cls):
    """A decorator to register a class as an exception"""
    try:
        name = cls.name or f"{__name__}.{cls.__name__}"
    except AttributeError:
        raise ValueError("Class to register must have a 'name' attribute")
    _register_exception_type(name, cls)
    return cls


@portable_exception
class ResurrectionError(NamedError):
    pass


@portable_exception
class DuplicationError(NamedError):
    pass


@portable_exception
class NonExistentError(NamedError):
    pass
