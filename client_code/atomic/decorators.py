# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import wraps

from .constants import SUBSCRIBE
from .contexts import ActionContext
from .registrar import get_registrar
from .rendering import active, call_queued, queued
from .subscribers import Render, Selector

__version__ = "0.0.1"


def _get_selector(fn, atom, prop):
    atom_registrar = get_registrar(atom)
    s = atom_registrar.selectors.get(prop)
    if s is None:
        s = atom_registrar.selectors[prop] = Selector(fn, atom, prop)
    return s


def selector(fn):
    """decorate a method as a selector whenever it needs to do some computation based on atom attributes
    This decorate can only be used on an atom method
    You should never update an atom within a selector
    A selector can be decorated with @property
    """
    prop = fn.__name__

    @wraps(fn)
    def selector_wrapper(atom):
        selector = _get_selector(fn, atom, prop)
        return selector.value

    return selector_wrapper


def action(_fn=None, **kws):
    """Whenever a method does multiple updates use the @action decorator
    only when the method has finished will renders methods be re-rendered
    and selector methods be re-computed
    action can be called with kws like @action(update_db=True)
    any kws will be added to the action as attributes
    useful when an action is passed to a function decorated with @susbcribe
    """
    if _fn is None:
        return lambda _fn: action(_fn, **kws)
    for k, v in kws.items():
        setattr(_fn, k, v)

    @wraps(_fn)
    def action_wrapper(*args, **kws):
        with ActionContext(_fn):
            res = _fn(*args, **kws)
        return res

    return action_wrapper


def subscribe(f):
    """A subscriber is called after all re-renders resulting from a series of actions
    a subscriber takes a single argument - the tuple of actions that caused the re-render
    This might be used to update local storage based on the actions that were performed
    """
    active[SUBSCRIBE] += (f,)
    return f


class render:
    """a decorator typically used above a method in a form
    if used on a form render methods will only execute on the show event
    if used as a top level function it can be used to update a database whenever an atom attribute changes

    a render should access all selectors and atom attributes that it depends on
    i.e. don't access some attributes within branching logic (if statements)
    """

    def __new__(cls, _fn=None, **kws):
        if _fn is None:
            return lambda _fn: render(_fn, **kws)
        return object.__new__(cls)

    def __init__(self, _fn, bound=None):
        self.f = _fn
        self.bound = bound

    def __call__(self, *args, **kws):
        # each call creates a new renderer
        return Render(self.f, args, kws, self.bound).render()

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        method = self.f.__get__(obj, cls)
        bound = self.bound or obj
        return render(method, bound=bound)


def autorun(f, bound=None):
    """create render function that is called immediately.
    Optionally provide a component to bind this method to"""
    if bound is None:
        try:
            bound = f.__self__
        except AttributeError:
            pass
    return render(f, bound=bound)()
