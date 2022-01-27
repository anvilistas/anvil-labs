# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from ..exceptions import NamedError, portable_exception

__version__ = "0.0.1"


@portable_exception
class ResurrectionError(NamedError):
    pass


@portable_exception
class DuplicationError(NamedError):
    pass


@portable_exception
class NonExistentError(NamedError):
    pass


@portable_exception
class AuthorizationError(NamedError):
    pass


@portable_exception
class UnregisteredClassError(NamedError):
    pass


@portable_exception
class InvalidUIDError(NamedError):
    pass
