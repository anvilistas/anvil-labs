Unit Testing
=======================
A component that displays all unit test modules, classes, and methods that allows you to run those tests.
When you run a test module or test class, you see the pass or fail results as icons. When you run a test method,
you get the full traceback if it fails.

Define your unit tests on the client side using the ``unittest`` module which is supported in Skulpt.
Note that only the ``assert`` unittest method works. ``assertEqual``, ``assertNotEqual``, etc. do not fail in Skulpt
if the test fails.

Here's an example of a client side test module called ``test_unittest``:

.. code-block:: python

    """This is a test module."""
    import unittest


    class TestClass(unittest.TestCase):
        """This is a testclass"""

        def test_method_1(self):
            """Test Method 1."""
            self.assert (True)

It is recommended to use this component in code like so in your 'home' form:

.. code-block:: python

    import anvil
    from anvil_labs.ClientTestComponent import ClientTestComponent

    class HomeForm(HomeFormTemplate):
        def __init__(self, **properties):
            # Set Form properties and Data Bindings.
            self.init_components(**properties)

            # Create a button called btn_test on the nav bar
            # that is invisible by default.
            # Also set the click event handler to self.open_tests

            test_envs = ["Debug for dev@email.com", "App Server"]
            if anvil.app.environment.name in test_envs:
                self.btn_test.visible = True

        def open_tests(self, **event_args):
            from .. import test_unittest
            self.add_component(
                ClientTestComponent(
                    test_modules=[test_unittest],
                    card_roles=['tonal-card', 'elevated-card', 'elevated-card'],
                    icon_size=30,
                    btn_role='filled-button'
                )
            )

Properties
----------

:test_modules: Object

    List of imported test modules. Pass in code.

:card_roles: List

    Roles for Module, TestClass, and TestMethod cards.

:icon_size: Number

    Size of the 'success' or 'fail' icons.

:btn_role: String

    Role for 'run tests' buttons.
