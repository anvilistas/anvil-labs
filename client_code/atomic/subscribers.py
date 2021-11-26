# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil
from anvil.js import get_dom_node

from .constants import RENDER, SELECTOR
from .contexts import RenderContext, SelectorContext
from .rendering import register, request
from .utils import get_atom_prop_repr

__version__ = "0.0.1"


class Subscriber:
    """base class knows how to register and unregister"""

    mode = None

    def __init__(self):
        self.dependents = set()
        self.atom_registrar_prop = set()

    def add_dependent(self):
        raise NotImplementedError

    def register(self, atom_registrar, prop):
        self.atom_registrar_prop.add((atom_registrar, prop))

    def unregister(self, atom_registrar, prop):
        self.atom_registrar_prop.discard((atom_registrar, prop))


class Render(Subscriber):
    """a render subscriber is created for each call to a decorated render method"""

    mode = RENDER

    def __init__(self, f, args, kws, bound=None):
        super().__init__()
        self.f = f
        self.args = args
        self.kws = kws
        self.bound = (
            bound if bound is not None and isinstance(bound, anvil.Component) else None
        )

    def add_dependent(self, parent):
        # I depend on my parent
        parent.dependents.add(self)

    def maybe_delay(self, immediate=False):
        bound = self.bound
        if bound is None:
            return False
        try:
            bound.remove_event_handler("show", self.render)
            bound.remove_event_handler("x-force-render", self.render)
        except LookupError:
            pass

        delay = not get_dom_node(bound).isConnected and not immediate
        if delay:
            bound.add_event_handler("show", self.render)
            bound.add_event_handler("x-force-render", self.render)
        return delay

    def render(self, event_name=None, **event_args):
        immediate = event_name == "x-force-render"
        if self.maybe_delay(immediate=immediate):
            return
        with RenderContext(self):
            return self.f(*self.args, **self.kws)

    def __repr__(self):
        return self.f.__qualname__


MISSING = object()
INITIAL = "initializing"
CACHE = "using cached"
RECOMPUTE = "recomputing"


class Selector(Subscriber):
    """A Selector subscriber is created once, when an atom calls a selector"""

    mode = SELECTOR

    def __init__(self, f, atom, prop):
        super().__init__()
        self.f = f.__get__(atom)
        self.atom = atom
        self.prop = prop
        self.cached = MISSING
        self.status = INITIAL

    def add_dependent(self, parent):
        # my parent depends on me
        self.dependents.add(parent)

    @property
    def value(self):
        # anytime our value is requested make renders/selectors depend on our property
        register(self.atom, self.prop)
        with SelectorContext(self):
            if self.cached is MISSING:
                self.update_cache()
            return self.cached

    def update_cache(self):
        self.cached = self.f()
        self.status = CACHE

    def compute(self):
        self.status = RECOMPUTE
        with SelectorContext(self):
            self.update_cache()
        request(self.atom, self.prop)
        # the compute happens within an update cycle
        # i.e. not part of the getattribute mechanism
        # any computations that depend on us must be requested

    def __repr__(self):
        return f"{self.status}: {get_atom_prop_repr(self.atom, self.prop)}"
