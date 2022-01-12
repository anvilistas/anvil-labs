# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import pytest

from client_code.historic.model import Event

__version__ = "0.0.1"


def test_event_type():
    with pytest.raises(ValueError):
        Event("hello", "world")
