# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import lru_cache

import anvil

from .constants import REACTION, RENDER, SELECTOR
from .contexts import ReactionContext, RenderContext, SelectorContext
from .rendering import active, register, request
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

    def dispose(self):
        for registrar, prop in self.atom_registrar_prop.copy():
            # the registrar will call our unregister method
            registrar.unregister(prop, self, self.mode)

    def register(self, atom_registrar, prop):
        self.atom_registrar_prop.add((atom_registrar, prop))

    def unregister(self, atom_registrar, prop):
        self.atom_registrar_prop.discard((atom_registrar, prop))


class Render(Subscriber):
    """a render subscriber is created for each call to a decorated render method"""

    mode = RENDER

    def __init__(self, f, args=None, kws=None, bound=None):
        super().__init__()
        self.f = f
        self.args = args or ()
        self.kws = kws or {}
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

        delay = (
            not anvil.js.get_dom_node(bound).isConnected
            and not immediate
            and not active[RENDER]
        )
        if delay:
            bound.add_event_handler("show", self.render)
            bound.add_event_handler("x-force-render", self.render)
        return delay

    def render(self, event_name=None, **event_args):
        immediate = event_name == "x-force-render"
        if self.maybe_delay(immediate=immediate):
            return
        with RenderContext(self):
            res = self.f(*self.args, **self.kws)
        return res

    def __repr__(self):
        return self.f.__qualname__


INITIAL = "initializing"
CACHE = "using cached"
RECOMPUTE = "recomputing"


class Selector(Subscriber):
    """A Selector subscriber is created once, when an atom calls a selector"""

    mode = SELECTOR

    def __init__(self, f, atom, prop):
        super().__init__()
        self.f = lru_cache(maxsize=16)(f.__get__(atom))
        self.atom = atom
        self.prop = prop
        self.status = INITIAL
        self.args = ()
        self.kws = {}

    def add_dependent(self, parent):
        # my parent depends on me
        self.dependents.add(parent)

    def compute_cached(self):
        with SelectorContext(self):
            cached = self.f(*self.args, **self.kws)
        self.status = CACHE
        return cached

    def __call__(self, *args, **kws):
        # anytime our value is requested make renders/selectors depend on our property
        # we don't use atom's __getattribute__ for registration since it doesn't register methods accessed
        # and we only want the registration to occur when we call the selector
        # this allows selectors to be used as the bind/writeback function
        register(self.atom, self.prop)
        self.args = args
        self.kws = kws
        return self.compute_cached()

    def compute(self):
        self.status = RECOMPUTE
        self.f.cache_clear()
        self.compute_cached()
        request(self.atom, self.prop)
        # the compute happens within an update cycle
        # i.e. not part of the getattribute mechanism
        # any computations that depend on us must be requested

    def __repr__(self):
        return f"{self.status}: {get_atom_prop_repr(self.atom, self.prop)}"


class Reaction(Subscriber):
    """a render subscriber is created for each call to a decorated render method"""

    mode = REACTION

    def __init__(self, depends_on, then_react, fire_immediatly=False, **options):
        super().__init__()
        self.depends_on = depends_on
        self.then_react = then_react
        self.options = options
        if fire_immediatly:
            return self.react()
        with ReactionContext(self):
            self.depends_on()

    def react(self):
        with ReactionContext(self):
            res = self.depends_on()
        if res is not None:
            self.then_react(res)
        else:
            self.then_react()

    def __repr__(self):
        return self.depends_on.__qualname__
