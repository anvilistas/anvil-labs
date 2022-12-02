# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


def enum(name, members):
    _ = type(name, (), {})()
    _.__dict__.update({member: member for member in members})
    return _
