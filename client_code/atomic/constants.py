# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from anvil import is_server_side

__version__ = "0.0.1"

REGISTRAR = "__atom_registrar__"

# MODES
SELECTOR = "selector"
ACTION = "action"
RENDER = "render"
SUBSCRIBE = "subscriber"
IGNORE = "ignore"
REACTION = "reaction"


SENTINEL = object()
CHANGE = "changing"
DELETE = "deleting"

IS_SERVER_SIDE = is_server_side()
