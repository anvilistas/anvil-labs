# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import wraps

from .constants import IS_SERVER_SIDE, SUBSCRIBE
from .contexts import ActionContext
from .registrar import get_registrar
from .rendering import active
from .subscribers import Reaction, Render, Selector
from .utils import MethodType, is_atom

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
    def selector_wrapper(atom, *args, **kws):
        selector = _get_selector(fn, atom, prop)
        return selector(*args, **kws)

    return fn if IS_SERVER_SIDE else selector_wrapper


class action:
    """Whenever a method does multiple updates use the @action decorator
    only when the method has finished will renders methods be re-rendered
    and selector methods be re-computed
    action can be called with kws like @action(update_db=True)
    any kws will be added to the action as attributes
    useful when an action is passed to a function decorated with @susbcribe
    """

    def __new__(cls, _fn=None, **kws):
        if _fn is None:
            return lambda _fn: action(_fn, **kws)
        return _fn if IS_SERVER_SIDE else object.__new__(cls)

    def __init__(self, _fn, **kws):
        for k, v in kws.items():
            setattr(_fn, k, v)
        self._f = _fn

    def __getattr__(self, attr):
        return getattr(self._f, attr)

    @property
    def atom(self):
        if type(self._f) is not MethodType:
            return None
        atom = self._f.__self__
        return atom if is_atom(atom) else None

    def __call__(self, *args, **kws):
        with ActionContext(self):
            res = self._f(*args, **kws)
        return res

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return action(self._f.__get__(obj, cls))

    def __repr__(self):
        return repr(self._f)


def subscribe(f):
    """A subscriber is called after all re-renders resulting from a series of actions
    a subscriber takes a single argument - the tuple of actions that caused the re-render
    This might be used to update local storage based on the actions that were performed
    """
    active[SUBSCRIBE] += (f,)
    return f


def unsubscribe(f):
    """remove a subscriber"""
    subscribers = active[SUBSCRIBE]
    i = subscribers.index(f)  # will raise ValueError
    active[SUBSCRIBE] = subscribers[:i] + subscribers[i + 1 :]


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
        return _fn if IS_SERVER_SIDE else object.__new__(cls)

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
    The function will be re-called anytime an attribute accessed within the function changes.
    Optionally provide a component to bind this method to.
    Similar to: render(fn)()

    Returns: a dispose function - when called to stop the autorun"""
    if bound is None and type(f) is MethodType:
        bound = f.__self__
    r = Render(f, bound=bound)
    r.render()
    return r.dispose


def reaction(depends_on_fn, then_react_fn, fire_immediately=False, **options):
    """a reaction takes two arguments: depends_on_fn and then_react_fn
    the depends_on_fn is used to determine the dependcies that the then_react_fn depends on
    when ever an atom attribute accessed in the depends_on_fn changes the then_react_fn is called.

    If the depends_on_fn returns a value other than None the return value will be passed to the then_react_fn.

    depends_on_fn fires immediately, but then_react_fn will only be called the next time a dependency changes.
    To call the then_react_fn function immediately set fire_immediately to True.

    Returns: a dispose function - when called stops any future reactions
    """
    r = Reaction(
        depends_on_fn, then_react_fn, fire_immediately=fire_immediately, **options
    )
    return r.dispose
