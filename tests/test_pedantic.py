# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import pytest

from client_code.pedantic import InList, validate

__version__ = "0.0.1"

valid_items = ["one", "two"]


@validate(another_item=InList(valid_items))
@validate(item=InList(valid_items))
class Thing:
    def __init__(self, item, another_item):
        self.item = item
        self.another_item = another_item


def test_valid_items():
    for item in valid_items:
        thing = Thing(item, item)
        assert thing.is_valid()


def test_invalid_item():
    with pytest.raises(ValueError):
        Thing("three", "three")
