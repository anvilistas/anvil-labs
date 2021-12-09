# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .constants import REGISTRAR, RENDER, SELECTOR

__version__ = "0.0.1"


class AtomRegistrar:
    """the registrar is responsible for registering and unregistering atom props to renderers/selectors
    as well as caching selectors associated with an atom"""

    def __init__(self, atom):
        self.atom = atom
        self.to_update = {RENDER: {}, SELECTOR: {}}
        self.selectors = {}

    def register(self, prop, subscriber, mode):
        subscriber_set = self.to_update[mode].setdefault(prop, set())
        if subscriber not in subscriber_set:
            subscriber_set.add(subscriber)
            subscriber.register(self, prop)
            return True

    def unregister(self, prop, subscriber, mode):
        to_update = self.to_update[mode].get(prop)
        if to_update is None:
            return
        to_update.discard(subscriber)
        subscriber.unregister(self, prop)
        if not to_update:
            self.to_update[mode].pop(prop)


_getattr = object.__getattribute__
_setattr = object.__setattr__


def add_registrar(atom):
    if get_registrar(atom) is None:
        _setattr(atom, REGISTRAR, AtomRegistrar(atom))


def get_registrar(atom):
    try:
        return _getattr(atom, REGISTRAR)
    except AttributeError:
        return None
