# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import anvil

import pytest

is_server_side = anvil.is_server_side
anvil.is_server_side = lambda: False  # so that atomic thinks we're client side

from client_code.atomic import (
    action,
    atom,
    autorun,
    bind,
    ignore_updates,
    portable_atom,
    render,
    selector,
    subscribe,
    unsubscribe,
    writeback,
)

anvil.is_server_side = is_server_side

__version__ = "0.0.1"


@atom
class CountAtom:
    value = 0

    @action
    def increment(self, n):
        self.value += n

    @action
    def set_count(self, n):
        self.value = n

    @selector
    def get_count(self):
        global count_computes
        count_computes += 1
        return self.value


count_atom = CountAtom()
count_subscribes = 0
count_actions = 0
count_renders = -1
count_computes = 0


def count_subscriber(actions):
    global count_actions, count_subscribes
    for a in actions:
        assert a.atom is count_atom
        count_actions += 1
    count_subscribes += 1


@render
def count_renderer():
    global count_renders
    count_atom.value
    count_renders += 1


def test_counter():
    assert count_atom.value == 0
    subscribe(count_subscriber)
    count_renderer()

    # test Base Action
    count_atom.value += 1
    assert count_atom.value == 1
    assert count_actions == 1
    assert count_subscribes == 1
    assert count_renders == 1

    # test decorated action
    count_atom.increment(2)
    assert count_atom.value == 3
    assert count_actions == 3  # one for the get_value and one for the base action
    assert count_subscribes == 2  # one for the get_value and one for the base action
    assert count_renders == 2

    # test selector
    assert count_atom.get_count() == 3
    assert count_computes == 1
    count_atom.get_count()
    assert count_computes == 1
    count_atom.increment(-count_atom.value)
    assert count_computes == 2
    assert count_atom.get_count() == 0
    assert count_computes == 2

    assert count_renders == 3
    unsubscribe(count_subscriber)


class FakeComponent:
    def __init__(self, value=None):
        self.value = value
        self.event_handlers = {}

    def add_event_handler(self, event, handler):
        self.event_handlers[event] = handler

    def raise_event(self, event):
        self.event_handlers[event]()


def test_bind():
    count_atom = CountAtom()
    c1 = FakeComponent()
    c2 = FakeComponent()

    bind(c1, "value", count_atom, "value")
    bind(c2, "value", count_atom.get_count)

    assert c1.value == c2.value == count_atom.value
    count_atom.value = 42
    assert c1.value == c2.value == 42
    count_atom.increment(1)
    assert c1.value == c2.value == 43
    c1.value = None
    assert count_atom.value is not None

    c3 = FakeComponent()
    writeback(c3, "value", count_atom, "value", ["change"])
    c3.value = 9
    assert count_atom.value != 9
    c3.raise_event("change")
    assert c1.value == c2.value == count_atom.value == 9

    c4 = FakeComponent()
    count_atom.value = 1
    writeback(c4, "value", count_atom.get_count, count_atom.set_count, ["change"])
    assert c1.value == c2.value == c3.value == c4.value == 1
    c4.value = 5
    c4.raise_event("change")
    assert c1.value == c2.value == c3.value == count_atom.value == 5


subscribe_db = {"todos": []}
autorun_db = {}


@portable_atom
class Todos:
    def __init__(self):
        self.todos = []
        self.selectors = 0

    @action(update_db=True)
    def add_todo(self, todo):
        self.todos.append(todo)

    @selector
    def get(self, attr, **kws):
        with ignore_updates:
            # update without triggering a render
            self.selectors += 1
        return getattr(self, attr, None)


todos_atom = Todos()


def update_db_subscriber(actions):
    if any(hasattr(action, "update_db") for action in actions):
        subscribe_db["todos"] = [dict(todo) for todo in todos_atom.todos]


@autorun
def update_db_renderer():
    autorun_db["todos"] = [{k: v for k, v in todo.items()} for todo in todos_atom.todos]


def test_todos():
    subscribe(update_db_subscriber)
    assert todos_atom.todos == subscribe_db["todos"] == autorun_db["todos"] == []
    todos_atom.add_todo({"completed": False, "description": "walk the dog"})
    todos_atom.add_todo({"completed": True, "description": "take out the bins"})
    assert todos_atom.todos == subscribe_db["todos"]
    assert todos_atom.todos == autorun_db["todos"]

    assert isinstance(todos_atom.todos, list)
    assert isinstance(todos_atom.todos[0], dict)
    assert type(todos_atom.todos) is not list
    assert type(todos_atom.todos[0]) is not dict

    # test dict view forces a render
    todos_atom.todos[0]["completed"] = True
    assert todos_atom.todos != subscribe_db["todos"]
    assert todos_atom.todos == autorun_db["todos"]
    todos_atom.todos[0]["completed"] = True

    unsubscribe(update_db_subscriber)

    with pytest.raises(ValueError):
        unsubscribe(update_db_subscriber)

    # test selector with multiple args
    assert todos_atom.selectors == 0
    todos_atom.get("todos", x=None)
    assert todos_atom.selectors == 1
    todos_atom.get("todos", x=None)
    assert todos_atom.selectors == 1
    todos_atom.get("selectors")
    assert todos_atom.selectors == 2
    todos_atom.get("selectors")
    todos_atom.get("todos", x=None)
    assert todos_atom.selectors == 2
    todos_atom.get("todos", x=1)
    assert todos_atom.selectors == 3
    todos_atom.add_todo({"completed": False, "description": "clean up my life"})
    assert todos_atom.selectors == 4
    assert todos_atom.get("todos") is todos_atom.todos

    with pytest.raises(TypeError) as e:
        todos_atom.get({})
    assert "unhashable" in str(e)


def test_bad_contexts():

    count_atom = CountAtom()

    @render
    def bad_render():
        count_atom.value = 3

    with pytest.raises(RuntimeError):
        bad_render()

    @selector
    def bad_selector(self):
        self.value = 4

    CountAtom.bad_selector = bad_selector

    with pytest.raises(RuntimeError):
        count_atom.bad_selector()

    del CountAtom.bad_selector

    @selector
    def ok_selector(self):
        with ignore_updates:
            self.value = None

    CountAtom.ok_selector = ok_selector

    count_atom.ok_selector()
    assert count_atom.value is None

    del CountAtom.ok_selector
