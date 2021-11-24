# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import partial

from .constants import ACTION, IGNORE, RENDER, SELECTOR
from .rendering import active, call_queued, log, queued


# ADDERS
def add_active(to_add, mode, conflicts=(), msg=""):
    if any(active[m] for m in conflicts):
        raise RuntimeError(msg)
    active[mode] += (to_add,)


def make_dependent(subscriber):
    if active[IGNORE]:
        return
    actives = active[subscriber.mode]
    if actives:
        subscriber.add_dependent(actives[-1])


# POP
def pop_active(mode):
    actives = active[mode]
    assert actives, "no " + mode + " to pop"
    active[mode] = actives[:-1]


class Context:
    """base context"""

    adder = None
    popper = None
    mode = None

    def __repr__(self):
        if type(self.context) is tuple:
            return repr(self.context)
        else:
            return f"{self.mode}: {self.context}"

    def __init__(self, context=None):
        self.context = context

    def _check_ignore(self):
        return not active[IGNORE] or self.mode is IGNORE

    def __enter__(self):
        log(lambda: self)
        if self._check_ignore():
            self.adder()
        return self

    def __exit__(self, *args):
        if self._check_ignore():
            self.popper()


class IgnoreUpdates(Context):
    """stops any renders/selectors being queued while updating an atom property
    This is most useful for lazy loading certain attributes of an atom"""

    def adder(self):
        active[IGNORE] += (self.context,)

    popper = staticmethod(partial(pop_active, IGNORE))
    mode = IGNORE


ignore_updates = IgnoreUpdates(True)


class ActionContext(Context):
    def adder(self):
        msg = "Cannot update an Atom or call an action from inside a selector or render method \
            - use `with ignore_updates:` if you really need to update an Atom attribute"
        add_active(self.context, ACTION, (SELECTOR, RENDER), msg)
        queued[ACTION] += (self.context,)

    def popper(self):
        pop_active(ACTION)
        if not active[ACTION]:
            call_queued()

    mode = ACTION


class RenderContext(Context):
    def adder(self):
        msg = "Cannot call a render method from inside a selector"
        make_dependent(self.context)
        add_active(self.context, RENDER, (SELECTOR,), msg)

    popper = staticmethod(partial(pop_active, RENDER))
    mode = RENDER


class SelectorContext(Context):
    def adder(self):
        make_dependent(self.context)
        add_active(self.context, SELECTOR)

    popper = staticmethod(partial(pop_active, SELECTOR))
    mode = SELECTOR
