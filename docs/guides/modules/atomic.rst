Atomic
======

Object-oriented state management.
The aim is to separate the state from the UI.
Atoms manage the state.
A form now has two jobs. It displays the state and hooks up events (like button clicks) to actions.
The atom's job is to manage the state.
Each atom is a global object, which any form can import.
By eliminating state from forms, there is no need to pass state up and down the form hierarchy.
It also makes testing easier, since we can test atoms in isolation.


Examples
--------

Some examples can be found at in this `clone link <https://anvil.works/build#clone:IN4YLWJBNNS2HHA6=KS6RVKNVD5IVN3MSKUMBMYCF>`_.

Counter
*******


.. code-block:: python

    # Create an atom that holds state
    from anvil_labs.atomic import atom, action, selector

    @atom
    class CountAtom:
        value = 0

        @selector
        def get_count(self):
            return self.value

        @action
        def update_count(self, increment):
            self.value += increment

    count_atom = CountAtom()

.. code-block:: python

    # Create a form to display the count
    from anvil_labs.atomic import render
    from ..atoms.count import count_atom

    class Count(CountTemplate):
        def __init__(self):
            self.display_count()

        @render
        def display_count(self):
            # I get called any time the get_count return value changes
            self.count_lbl.text = count_atom.get_count()

        def neg_btn_click(self, **event_args):
            count_atom.update_count(-1)

        def pos_btn_click(self, **event_args):
            count_atom.update_count(1)


In this example, whenever a button is clicked:

* the button event handler calls an ``action`` on the atom,
* which updates the state of the atom,
* which then updates any ``selectors`` that depend on that state change; and finally,
* any ``render`` methods that depend on those updates are re-rendered.


**Action** → **State change** → **Re-compute selectors** → **Call render methods**


Terminology
-----------

Action
******

An action is an expression/statement that updates the state of an atom.
Whenever the state changes, the atomic module invokes a render cycle.
We probably don't want each state change to invoke a render cycle;
sometimes it makes sense to combine state updates into a single action.
To combine actions into a single action, use the ``@action`` decorator.
Using the ``@action`` decorator means that the render cycle will only be invoked
after all actions within the decorated function have been completed.
The ``@action`` decorator can be used on any function and does not necessarily
need to be a method of an atom.

Selector
********

A ``selector`` is a method of an atom that returns a value based on the atom's state.
Essentially it is a getter method.
When a ``selector`` needs to do something expensive,
by say, combining various attributes of an atom, use the ``@selector`` decorator.
The return value from a decorated selector method is cached.
Whenever the atoms state changes, if the selector depends on that state,
the selector's return value will be re-computed.

You should never update the state (call an action) within a ``selector``.

Render
******

A ``render`` is any method/function that depends on the state of an atom,
or that depends on the return value of a ``selector``.

It's most commonly used on methods within forms, but a ``render`` can be used
outside of a form.

.. code-block:: python

    from anvil.js.window import document
    from anvil_labs.atomic import render

    @render
    def update_tab_title():
        document.title = count_atom.get_count()

    update_tab_title()

Note we might want to do this with the ``autorun`` function.
The above example is equivalent to.

.. code-block:: python

    from anvil_labs.atomic import autorun

    def update_tab_title():
        document.title = count_atom.get_count()

    autorun(update_tab_title)




To depend on the state of an atom, the
``render`` method must explicitly access that state.


.. code-block:: python

    # BAD Example
    class Count(CountTemplate):
        def __init__(self):
            self.display_count(count_atom.value)

        @render
        def display_count(self, count):
            self.count_lbl.text = count

In the above example, the ``display_count`` method does not explicitly access the ``count_atom.value`` attribute.
This means it does **not** depend on this attribute. The code should look like this:

.. code-block:: python

    # GOOD Example
    class Count(CountTemplate):
        def __init__(self):
            self.display_count()

        @render
        def display_count(self, count):
            self.count_lbl.text = count_atom.value



Accessing an attribute/selector implicitly subscribes the ``render`` method to changes in the state of those attributes/selectors.
Any time one of these attributes changes, the ``render`` method is invoked (re-rendered).

You should never update the state (call an action) within a ``render`` method.

If the render method is called by a component, it will only execute when the form is on the screen.
This prevents renders from happening for cached forms, or forms that are no longer active.

Atom
****

An ``atom`` is any object that knows how to register subscribers and request renders.
To create an atom, use the ``@atom`` decorator.

Whenever an attribute of an ``atom`` is a ``list`` or ``dict``,
the attribute will be converted to a ``ListAtom`` or ``DictAtom``.
Each is a subclass of ``list``/ ``dict`` and behave as you'd expect.
The only difference is that these classes know how to register subscribers and request renders when their state changes.


Subscriber
**********

A subscriber is an advanced feature. It's the final part of the render cycle.
After all renders have been completed any subscribers that were decorated with the ``@subscribe``
decorator will be called. A subscriber takes a single argument, a tuple of actions that were called to invoke the render cycle.

A reason to use a subscriber might be to update storage based on an action that was invoked.

Here's an example.

.. code-block:: python

    from anvil_extras.storage import indexed_db
    from anvil_labs.atomic import atom, action, subscribe

    @atom
    class Todos:
        def __init__(self):
            self.todos = indexed_db.get("todos", [])

        @action(update_db=True)
        def add_todo(self, todo):
            self.todos = self.todos + [todo]


    todos_atom = Todos()

    @subscribe
    def update_db_subscriber(actions):
        if any(hasattr(action, "update_db") for action in actions):
            indexed_db["todos"] = todos_atom.todos



The ``@action`` decorator can be used on any function or method.
If the decorator is used above a method then the ``atom`` used as the ``self`` argument
can be caught within a ``subscribe`` function

.. code-block:: python

    @subscribe
    def update_db_subscriber(actions):
        for action in actions:
            if hasattr(action, "update_db"):
                atom = action.atom
                break
        else:
            return

        # now use the atom do do something specific
        ...


Alternave Approaches to the subscriber

.. code-block:: python

    # ALTERNATIVE APPROACH 1 - use a render

    is_first_run = True
    @render
    def update_db_with_render():
        global is_first_run

        todos = [dict(todo) for todo in todos_atom.todos]
        # accessing the todos and each converting each todo to a dict
        # creates a depenency on the todos and each key of each todo
        # whenever these change this method is called

        if is_first_run:
            is_first_run = False
            return
        indexed_db["todos"] = todos

    update_db_with_render()

    # ALTERNATIVE APPROACH 2 - use autorun

    def update_db_with_render():
        # same code as above
        ...
    autorun(update_db_with_render)


    # ALTERNATIVE APPROACH 3 - use a reaction

    def update_db_with_reaction(todos):
        indexed_db["todos"] = todos

    reaction(lambda: [dict(todo) for todo in todos_atom.todos], update_db_with_reaction)
    # the first function sets up the dependencies
    # the return value of this function is passed to the reaction function
    # the reaction function is called only after the first change to any dependency



Bindings and Writeback
----------------------

It's not recommended to use anvil writebacks and data bindings with atoms.
This is because we can't control the render cycle.

Instead, there are two helper functions to create bindings and writebacks in code.

.. code-block:: python

    from anvil_labs.atomic import bind

    class Count(CountTemplate):
        def __init__(self):
            bind(self.count_lbl, "text", count_atom.get_count)
            # or bind it to an attribute of an atom
            bind(self.count_lbl, "text", count_atom, "value")


The bind method is equivalent to:

.. code-block:: python

    def bind(component, prop, atom_or_selector, attr=None):
        @render(bound=component)
        def render_bind():
            if callable(atom_or_selector):
                setattr(component, prop, atom_or_selector())
            elif isinstance(atom_or_selector, dict):
                setattr(component, prop, atom_or_selector[attr])
            else:
                setattr(component, prop, getattr(atom_or_selector, attr))

        render_bind()

Note the render decorator can take a bound parameter.
This means that the render won't fire if the component is not on the screen.
This is not necessary when using the render decorator on a form method.

A writeback is similar to a bind, but a list of events must be provided.


.. code-block:: python


    writeback(self.check_box, "checked", self.item, "completed", events=["change"])


Alternatively, the writeback can be called with a selector in place of the atom and an action in place of the atom attribute.
If the selector/action call signature is used, the action must take a single argument (the updated property of the component).

.. code-block:: python

    writeback(component, prop, atom, attr, events)
    writeback(component, prop, selector, action, events)




API
---

.. function:: set_debug(debug=False)

    Show logging output for the module

.. decorator:: atom

    Create an atom class. An atom class knows how to register subscribers and
    request re-renders when its state changes.

.. decorator:: portable_atom

    Create an atom class which is also a portable class. It is recommended to use the
    ``@portable_atom`` decorator over a combination of ``@atom`` and ``@portable_class``.

.. decorator:: render
               render(bound=None)

    Use the ``render`` decorator anytime you want a function to depend on atom attributes or selectors.
    In a ``render`` method the attributes must be accessed explicitly.
    Whenever one of the attributes of the atom changes, the ``render`` method will be invoked.


.. decorator:: action
               action(**kws)

    The action decorator should be used above any method that you want to combine actions into a single action.
    A base action changes the state of an atom.
    When calling a function decorated with the ``@action`` decorator, the render cycle will be invoked only after
    all actions within the function have been executed.
    It's worth noting that the decorator doesn't need to be used unless you want to combine state updates into a single action.
    In the counter example, the action decorator is unnecessary, since there is only a single
    state update within the function (updating the ``.value`` property)

.. decorator:: selector

    The selector decorator can only be used on methods within an atom. Its utility is caching the return value and
    a selector subscribes to atom attributes in a similar way to renders.
    If any attribute changes, the cached value will be re-computed.
    It's worth noting that the selector decorator is unnecessary on methods where accessing the attribute is cheap.
    In the counter example, the selector is unnecessary and adds little to the implementation.

.. function:: autorun(fn)
              autorun(fn, bound=None)

    Similar to ``render(fn)()``. Any atom attributes accessed within the body of the function will
    trigger a new call to the function when changed.

    Calling ``autorun`` returns a dispose function.
    When the dispose function is called it stops any future renders of this ``autorun`` function.

    ``autorun`` can be used as a decorator - but note that the returned function is not the original function but the dipsose function.


.. function:: reaction(depends_on_fn, then_react_fn)
              reaction(depends_on_fn, then_react_fn, fire_immediately=False)

    a ``reaction`` is similar to a ``render``.
    Changes in the ``depends_on_fn`` will force the ``then_react_fn`` to be called.
    The ``depends_on_fn`` is a function that takes no args.
    It should access any attributes that, when changed, should result in the call to the ``then_react_fn``.
    If ``depends_on_fn`` returns a value that is not ``None``, this value will be passed to the ``then_react_fn``.

    ``depends_on_fn`` will fire immediately. But the ``then_react_fn`` is only called the next time a dependency changes.
    To call the ``then_react_fn`` immediately set ``fire_immediately=True``.

    It would be rare to need to use this function.
    However in cases where you want to react to a change in an atom's state
    that may result in subsquent change in another atom's state a reaction may be useful.
    It can also be used as an alternative to ``autorun`` or ``render``.

    See the example above for alternative approaches to upating ``indexed_db``

    The reaction method returns a dispose function that can be called when you want to stop reactions.


.. decorator:: subscribe

    A subscriber is called after all re-renders resulting from a series of actions
    a subscriber takes a single argument - the tuple of actions that caused the re-render.
    See examples for use cases.

.. function:: unsubscribe(f)

    Stop a subscriber from running.

.. class:: DictAtom

    A subclass of ``dict``. Any attribute within an atom that is a ``dict`` will be converted to a ``DictAtom``.
    This allows render methods to depend on keys of dicts within the atom's state.

.. class:: ListAtom

    A subclass of ``list``. Any attribute within an atom that is a ``list`` will be converted to a ``ListAtom``.
    Renders that depend on the ``ListAtom`` will only be invoked if the ``ListAtom`` changes
    through methods like ``remove()``, ``clear()`` etc.

.. class:: Atom(**kws)

    A portable atom class that can be called with kwargs. Each kwarg will become an attribute of the atom.
    Useful if you prefer to access attributes rather than keys of a ``DictAtom``.

    e.g. ``todo_atom = Atom(done=False, description='walk the dog')``


.. attribute:: ignore_updates

    This can be used as a context manager (using ``with``) to update an atom without invoking a render cycle.
    A reason to use this decorator is to lazy load an atom property.
    Use with caution.



Gotchas and advanced concepts
-----------------------------

My component isn't updating
***************************

Make sure that you have used the render decorator and that you have called this method from the ``__init__`` function.

Why don't you use ``self.init_components(**properties)`` in the example?
************************************************************************

The primary job of ``init_components`` is to set up data bindings.
But since we don't have any data bindings, we don't need to use this method.
Note that ``init_components`` does more work when used within a custom component.


How do I lazy load an attribute?
********************************

You can use the ``ignore_updates`` decorator to prevent actions invoking render cycles.
And since calling an action within a render or selector is not allowed it becomes necessary.

.. code-block:: python

    import anvil.server
    from anvil_labs.atomic import atom, ignore_updates, selector

    @atom
    class Todos:
        def __init__(self):
            self._todos = None

        @property
        @selector
        def todos(self):
            if self._todos is None:
                with ignore_updates:
                    self._todos = anvil.server.call("get_todos")
            return self._todos


Alternatively, you can call an action, ensuring that the action is not called inside a render/selector

.. code-block:: python

    from atoms import todos_atom

    class Form1(Form1Template):
        def __init__(self, **properties):
            # fetch_todos is an action that calls the server if it needs to
            todos_atom.fetch_todos()
            self.display_todos()



My UI is taking a long time to update
*************************************

That might be because you are calling a server function within an action.
The fetch example is a good example of how to update the UI while you make a call.

.. code-block:: python

    @atom
    class Fetch:
        value = None
        loading = False

        @action
        def set_status(self, value, loading=False):
            self.value = value
            self.loading = loading

        def do_fetch(self):
            self.set_status(None, loading=True)
            ret = anvil.server.call_s("do_fetch")
            self.set_status(ret, loading=False)

        @selector
        def get_info(self):
            return self.value, self.loading


    fetch_atom = Fetch()


``do_fetch`` is not an action, but ``set_status`` is an action.
``set_status`` is cheap and so the UI updates quickly.
Each call to ``set_status`` invokes a render cycle.
When ``loading`` is ``True`` the UI can disable a button while we call the server function.



How do I work with anvil data tables?
*************************************

We're working on it.
