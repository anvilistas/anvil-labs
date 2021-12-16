# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import datetime as dt

import anvil.server

from .pedantic import in_list, validated

__version__ = "0.0.1"


@anvil.server.portable_class
@in_list("event_type", ["creation", "change", "termination"])
@validated
class Event:
    def __init__(self, event_type, affected, recorded_at=None, occurred_at=None):
        self.event_type = event_type
        self.affected = affected
        self.recorded_at = recorded_at if recorded_at is not None else dt.datetime.now()
        self.occurred_at = occurred_at if occurred_at is not None else dt.datetime.now()
