# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from anvil_extras import logging

__version__ = "0.0.1"

LOGGER = logging.Logger("anvil_labs.historic", level=logging.INFO)


def set_debug(with_debug):
    levels = {True: logging.DEBUG, False: logging.INFO}
    LOGGER.level = levels[with_debug]


def set_log_level(level):
    LOGGER.level = level
