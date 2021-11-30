# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .atoms import DictAtom, ListAtom, atom
from .contexts import ignore_updates
from .decorators import action, autorun, render, selector, subscribe
from .helpers import bind, set_debug, writeback

__version__ = "0.0.1"


@atom
class Atom:
    """a simple class that can be instantiated with kws
    and create a dict like atom with easy attribute access"""

    def __init__(self, **kws):
        for key, val in kws.items():
            object.__setattr__(self, key, val)
