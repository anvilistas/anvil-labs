# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from functools import lru_cache, partial

from .decorators import render_call
from .rendering import log


def set_debug(is_debug=True):
    """if set to true - logging messages will be output to the console"""
    log.is_debug = is_debug


def writeback(component, prop, atom_or_selector, attr_or_action=None, events=()):
    """create a writeback between a component property and an atom attribute
    or bind the property to an atom selector and call an action when the component property is changed
    events - should be a single event str or a list of events
    If no events are provided this is the equivalent of a data-binding with no writeback
    """
    atom, attr = atom_or_selector, attr_or_action
    if type(events) is str:
        events = [events]
    if isinstance(atom, dict):
        assert attr is not None, "if a dict atom is provided the attr must be a str"
        getter = partial(atom.__getitem__, attr)
        setter = partial(atom.__setitem__, attr)
    elif callable(atom):
        getter = atom
        setter = attr
    else:
        assert attr is not None, "if an atom is provided the attr must be a str"
        getter = partial(getattr, atom, attr)
        setter = partial(setattr, atom, attr)

    def render_component():
        setattr(component, prop, getter())

    render_component.__name__ = render_component.__qualname__ = (
        type(component).__name__ + "." + prop
    )

    def do_action(**event_args):
        setter(getattr(component, prop))

    for event in events:
        component.add_event_handler(event, do_action)

    render_call(render_component, bound=component)


def bind(component, prop, atom_or_selector, attr=None):
    """create a data-binding between an component property and an atom and its attribute (or a selector)"""
    # we could support methods here but it's better to be explicit and call selectors inside render methods
    # accessing an atom property necessarily creates a depenedency on the current render context
    # so better not to encourage accessing a selector outside of the desired render context
    return writeback(component, prop, atom_or_selector, attr)
