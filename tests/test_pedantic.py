# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import pytest

from client_code.pedantic import in_list

__version__ = "0.0.1"

valid_items = ["one", "two"]


@in_list("item", valid_items)
class Thing:
    def __init__(self, item):
        self.item = item


def test_valid_items():
    for item in valid_items:
        Thing(item)


def test_invalid_item():
    with pytest.raises(ValueError):
        Thing("three")
