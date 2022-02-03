# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import datetime as dt

from anvil.server import portable_class

__version__ = "0.0.1"


class _Event:
    def __init__(self, affected, recorded_at=None, occurred_at=None):
        self.affected = affected
        self.recorded_at = recorded_at if recorded_at is not None else dt.datetime.now()
        self.occurred_at = occurred_at if occurred_at is not None else dt.datetime.now()


@portable_class
class Creation(_Event):
    pass


@portable_class
class Change(_Event):
    pass


@portable_class
class Termination(_Event):
    pass
