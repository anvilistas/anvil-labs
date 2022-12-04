# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .locales.en import error_map as default_error_map

__version__ = "0.0.1"


def get_error_map():
    return default_error_map


def set_error_map(map):
    global default_error_map
    default_error_map = map
