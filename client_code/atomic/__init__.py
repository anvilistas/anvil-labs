# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .atoms import DictAtom, ListAtom, atom, portable_atom
from .contexts import ignore_updates
from .decorators import action, autorun, render, selector, subscribe, unsubscribe
from .helpers import bind, set_debug, writeback

__version__ = "0.0.1"


@portable_atom
class Atom:
    """a portable atom class that can be instantiated with kws.
    Create a dict like atom with easy attribute access
    e.g. todo_atom = Atom(done=False, description='walk the dog')"""

    def __init__(self, **kws):
        for key, val in kws.items():
            object.__setattr__(self, key, val)
