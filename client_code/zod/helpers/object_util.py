# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


def merge_shapes(a, b):
    return {**a, **b}


def getitem(mapping, item, default):
    try:
        return mapping[item]
    except LookupError:
        return default
