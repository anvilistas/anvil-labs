# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .constants import ACTION, IGNORE, RENDER, SELECTOR, SUBSCRIBE
from .registrar import get_registrar
from .utils import get_atom_prop_repr

# STATE
active = {ACTION: (), SELECTOR: (), RENDER: (), SUBSCRIBE: (), IGNORE: ()}
queued = {SELECTOR: frozenset(), RENDER: frozenset(), ACTION: ()}


# LOGGING
def log(fn):
    indent = "    " * (
        len(active[SELECTOR]) + len(active[RENDER]) + len(active[IGNORE])
    )
    if log.is_debug:
        print(f"{indent}{fn()}")


log.is_debug = False


def register(atom, prop):
    """if there is an active selector or render
    we asks the atom registrar to register a relationship between an atom and the attribute being accessed
    """
    if active[IGNORE]:
        return
    # check selectors first since you can't call a render inside a selctor
    # but you can call a selector from inside a render
    if active[SELECTOR]:
        mode = SELECTOR
    elif active[RENDER]:
        mode = RENDER
    else:
        return
    current = active[mode][-1]
    registrar = get_registrar(atom)
    registered = registrar.register(prop, current, mode)
    if registered:
        log(lambda: f"depends on: {get_atom_prop_repr(atom, prop)}")


def remove_atom_prop_relationship(subscriber, mode):
    """
    We ask the atom registrar to unregister a relationship between a render and an atom attribute.
    We only do this with render subscribers.
    """
    assert mode is RENDER
    registrars_props = subscriber.atom_registrar_prop
    for registrar, prop in registrars_props.copy():
        registrar.unregister(prop, subscriber, mode)


def remove_dependents(root, queue, mode, seen):
    """
    take dependents from a root subscriber and remove them from the subscriber queue
    """
    if root in seen:
        return queue
    seen.add(root)
    dependents = root.dependents
    if mode is RENDER:
        root.dependents = set()
        remove_atom_prop_relationship(root, mode)
    if not dependents:
        return queue
    queue -= dependents
    for dependent in dependents:
        queue = remove_dependents(dependent, queue, mode, seen)
    return queue


def get_to_queue(atom_registrar, prop, mode):
    """get the renders/selectors that depend on a particular atom attribute"""
    return frozenset(atom_registrar.to_update[mode].get(prop, []))


def queue_subscribers(atom_registrar, prop, mode):
    """update the current queue of subscribers with a new queue, removing dependent subscribers"""
    to_queue = get_to_queue(atom_registrar, prop, mode)
    queue = queued[mode] | to_queue
    seen = set()
    for subscriber in to_queue:
        queue = remove_dependents(subscriber, queue, mode, seen)
    return queue


def request(atom, prop):
    """when an attribute of an atom is accessed we update the queues based on the subscribers registered"""
    if active[IGNORE]:
        return
    atom_registrar = get_registrar(atom)
    queued_renders = queue_subscribers(atom_registrar, prop, RENDER)
    queued_selectors = queue_subscribers(atom_registrar, prop, SELECTOR)
    queued[RENDER], queued[SELECTOR] = queued_renders, queued_selectors


def call_render_queue():
    """this should call the most parent renders"""
    queue, queued[RENDER] = queued[RENDER], frozenset()
    for render in queue:
        render.render()
    assert not queued[RENDER]


def call_selector_queue():
    """this will call the most child selector
    child selectors will then request calls to selectors that depend on them
    """
    for _ in range(1000):
        if not queued[SELECTOR]:
            return
        queue, queued[SELECTOR] = queued[SELECTOR], frozenset()
        for selector in queue:
            selector.compute()
    else:
        raise RuntimeError("Suspected infinite loop from selectors")


def call_action_queue():
    """any registered subscribers will be called after all renders have taken place
    they get passed a tuple of actions that were used in this render round"""
    actions, queued[ACTION] = queued[ACTION], ()
    if not actions:
        return
    for subscriber in active[SUBSCRIBE]:
        subscriber(actions)


def call_queued():
    """calls all the queued subscribers - called after all actions have finished"""
    selector_queue = queued[SELECTOR]
    call_selector_queue()
    render_queue = queued[RENDER]
    call_render_queue()
    call_action_queue()
    if log.is_debug and (selector_queue or render_queue):
        print()
