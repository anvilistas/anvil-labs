# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas


from .constants import ACTION, IGNORE, REACTION, RENDER, SELECTOR
from .rendering import active, call_queued, log, queued

__version__ = "0.0.1"


class Context:
    """base context"""

    mode = None

    def __init__(self, context=None):
        self.context = context

    def __repr__(self):
        if type(self.context) is tuple:
            return repr(self.context)
        else:
            return f"{self.mode}: {self.context}"

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

    def adder(self):
        raise NotImplementedError

    def popper(self):
        raise NotImplementedError

    def add_active(self, conflicts=(), msg=""):
        mode = self.mode
        if any(active[m] for m in conflicts):
            raise RuntimeError(msg)
        active[mode] += (self.context,)

    def pop_active(self):
        mode = self.mode
        actives = active[mode]
        assert actives, "no " + mode + " to pop"
        active[mode] = actives[:-1]

    def make_dependent(self):
        if active[IGNORE]:
            return
        actives = active[self.mode]
        if actives:
            self.context.add_dependent(actives[-1])


class IgnoreUpdates(Context):
    """stops any renders/selectors being queued while updating an atom property
    This is most useful for lazy loading certain attributes of an atom"""

    mode = IGNORE
    adder = Context.add_active
    popper = Context.pop_active


ignore_updates = IgnoreUpdates(True)


class ActionContext(Context):
    mode = ACTION

    def adder(self):
        msg = (
            "Cannot update an Atom or call an action from inside a selector or"
            "render method - use `with ignore_updates:`"
            " if you really need to update an Atom attribute"
        )
        self.add_active((SELECTOR, RENDER, REACTION), msg)
        queued[ACTION] += (self.context,)

    def popper(self):
        self.pop_active()
        if not active[ACTION]:
            call_queued()


class RenderContext(Context):
    mode = RENDER

    def adder(self):
        msg = "Cannot call a render method from inside a selector"
        self.make_dependent()
        self.add_active((SELECTOR,), msg)

    popper = Context.pop_active


class SelectorContext(Context):
    mode = SELECTOR

    def adder(self):
        self.make_dependent()
        self.add_active()

    popper = Context.pop_active


class ReactionContext(Context):
    # note the ReactionContext only applies to the depends_on_fn call
    # There should only be attribute access
    # and selector method calls within this context
    mode = REACTION

    def adder(self):
        msg = (
            "The reaction depends_on_fn should only access atom attributes."
            "Calling a depends_on_fn from inside a selector,"
            " render or other depends_on_fn is invalid"
        )
        self.add_active((SELECTOR, RENDER, REACTION), msg)

    popper = Context.pop_active
