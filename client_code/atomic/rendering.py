# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from .constants import ACTION, IGNORE, REACTION, RENDER, SELECTOR, SUBSCRIBE
from .registrar import get_registrar
from .utils import get_atom_prop_repr

__version__ = "0.0.1"

# STATE
active = {ACTION: (), REACTION: (), SELECTOR: (), RENDER: (), SUBSCRIBE: (), IGNORE: ()}
queued = {ACTION: (), REACTION: frozenset(), SELECTOR: frozenset(), RENDER: frozenset()}


# LOGGING
def log(fn):
    if not log.is_debug:
        return
    indent = sum(len(active[v]) for v in (SELECTOR, RENDER, REACTION, IGNORE))
    print(f"{'    ' * indent}{fn()}")


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
    elif active[REACTION]:
        mode = REACTION
    else:
        return
    current = active[mode][-1]
    registrar = get_registrar(atom)
    if registrar is None:
        return
    registered = registrar.register(prop, current, mode)
    if registered:
        log(lambda: f"depends on: {get_atom_prop_repr(atom, prop)}")


def remove_atom_prop_relationship(subscriber, mode):
    """
    We ask the atom registrar to unregister a relationship between a render and an atom attribute.
    We only do this with render subscribers.
    """
    assert mode in (RENDER, REACTION)
    subscriber.dispose()


def remove_dependents(root, queue, mode, seen):
    """
    take dependents from a root subscriber and remove them from the subscriber queue
    """
    if root in seen:
        return queue
    seen.add(root)
    dependents = root.dependents
    if mode is not SELECTOR:
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
    if atom_registrar is None:
        return
    queued.update(
        {
            REACTION: queue_subscribers(atom_registrar, prop, REACTION),
            RENDER: queue_subscribers(atom_registrar, prop, RENDER),
            SELECTOR: queue_subscribers(atom_registrar, prop, SELECTOR),
        }
    )


def call_render_queue():
    """this should call the most parent renders"""
    queue, queued[RENDER] = queued[RENDER], frozenset()
    for render in queue:
        render.render()
    assert not queued[RENDER]


def call_queue_repeatedly(mode, update):
    """
    calling selectors and reactions may lead to more queued selectors and reactions
    child selectors are called first which will then queue renders from parent/dependent selectors
    the then_react method can cause an action which could then create another reaction
    """
    for _ in range(1000):
        if not queued[mode]:
            return
        queue, queued[mode] = queued[mode], frozenset()
        for item in queue:
            update(item)
    else:
        raise RuntimeError(f"Suspected infinite loop from {mode}s")


def call_subscriber_queue():
    """any registered subscribers will be called after all renders have taken place
    they get passed a tuple of actions that were used in this render round"""
    actions, queued[ACTION] = queued[ACTION], ()
    if not actions:
        return
    for subscriber in active[SUBSCRIBE]:
        subscriber(actions)


num_calls = 0


def call_queued():
    """calls all the queued subscribers - called after all actions have finished"""
    global num_calls
    num_calls += 1
    if num_calls > 1000:
        raise RuntimeError(
            "Queued 1000 update cycles without completing - suspected infinte loop"
        )
    has_queued = log.is_debug and (
        queued[SELECTOR] or queued[REACTION] or queued[RENDER]
    )
    call_queue_repeatedly(SELECTOR, lambda s: s.compute())
    call_queue_repeatedly(REACTION, lambda r: r.react())
    call_render_queue()
    call_subscriber_queue()
    if has_queued and num_calls:
        print()
    num_calls = 0
