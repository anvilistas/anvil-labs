NonBlocking
===========

Call function in a non-blocking way.

Examples
--------

Call a server function
**********************

After making updates on the client, call a server function to update the database.
In this example, we don't care about the return.


.. code-block:: python

    from anvil_labs.non_blocking import call_server_async

    def button_click(self, **event_args):
        self.update_database()
        self.open_form("Form1")

    def update_database(self):
        # Unlike anvil.server.call we do not wait for the call to return
        call_server_async("update", self.item)


If you care about the return value, you can provide handlers.

.. code-block:: python

    from anvil_labs.non_blocking import call_server_async

    def handle_result(self, res):
        print(res)
        Notification("successfully saved").show()

    def handle_error(self, err):
        print(err)
        Notification("there was a problem", style="danger").show()

    def update_database(self, **event_args):
        call_server_async("update", self.item).on_result(self.handle_result, self.handle_error)
        # Equivalent to
        async_call = call_server_async("update", self.item)
        async_call.on_result(self.handle_result, self.handle_result)
        # Equivalent to
        async_call = call_server_async("update", self.item)
        async_call.on_result(self.handle_result)
        async_call.on_error(self.handle_error)


Interval
********

Create a Timer-like object in code without worrying about components.

The function will run repeatedly after each delay.
This means setting the delay to 0 will cause the function to run every 0 seconds 😬.
To kill the Interval set the delay to None or call the ``clear()`` method.


.. code-block:: python

    from anvil_labs.non_blocking import Interval

    i = 0
    def do_heartbeat():
        global heartbeat, i
        if i >= 42:
            heartbeat.delay = None
            # equivalent to heartbeat.clear()
        print("da dum")
        i += 1

    heartbeat = Interval(do_heartbeat, delay=1)


Timeout
********

Create a Timer-like object in code without worrying about components.
A timeout will only run once after the delay.
To kill the Timeout set the delay to ``None`` or call the ``clear()`` method.

A Timeout is particularly useful for pending saves

.. code-block:: python

    from anvil_labs.non_blocking import Interval

    pending = []

    def do_save():
        global pending
        pending, saves = [], pending
        if not saves:
            return
        anvil.server.call_s("save", saves)

    save_timeout = Timeout(do_save)

    def on_save(saves):
        global pending
        pending.extend(saves)
        save_timeout.delay = 1

    # calling on_save repeatedly will reset the delay to do_save


API
---

.. function:: call_async(fn, *args, **kws)

    Returns an ``AyncCall`` object. The *fn* will be called in a non-blocking way.

.. function:: call_server_async(fn_name, *args, **kws)

    Returns an ``AyncCall`` object. The server function will be called in a non-blocking way.

.. function:: wait_for(async_call_object)

    Blocks until the ``AsyncCall`` object has finished executing.

.. class:: AyncCall

    Don't call this directly, instead use the above functions.

    .. method:: on_result(self, result_handler, error_handler=None)

        Provide a result handler to handle the return value of the non-blocking call.
        Provide an optional error handler to handle the error if the non-blocking call raises an exception.
        Both handlers should take a single argument.

        Returns ``self``.

    .. method:: on_error(self, error_handler)

        Provide an error handler that will be called if the non-blocking call raises an exception.
        The handler should take a single argument, the exception to handle.

        Returns ``self``.

    .. method:: await_result(self)

        Waits for the non-blocking call to finish executing and returns the result.
        Or raises an exception if the non-blocking call raised an exception.

    .. property:: result

        If the non-blocking call has not yet completed, raise a ``RuntimeError``.

        If the non_blocking call has completed returns the result.
        Or raises an exception if the non-blocking call raised an exception.

    .. property:: error

        If the non-blocking call has not yet completed, raise a ``RuntimeError``.

        If the non-blocking call raised an exception the exception raised can be accessed using the ``error`` property.
        The error will be ``None`` if the non-blocking call returned a result.

    .. property:: set_status

        One of ``"PENDING"``, ``"FULFILLED"``, ``"REJECTED"``


.. class:: Interval(fn, delay=None)

    Create an interval that will call a function every delay seconds.
    If the delay is ``None`` the Interval will stop calling the function.

    A delay of ``0`` means the function will be called every 0 seconds!

    Functions executed by an interval are non-blocking.

    .. attribute:: delay

        change the interval to ``None`` or an ``int`` / ``float`` in seconds.
        If the delay is ``None``, the function will no longer fire.

    .. method:: clear(self)

        Equivalent to ``my_interval.delay = None``

.. class:: Timeout(fn, delay=None)

    Create a timeout that will call a function after delay seconds.
    If the delay is ``None`` the timeout will stop calling the function.

    A delay of ``0`` means the function will be called immediately!

    Functions executed by a timeout are non-blocking.

    .. attribute:: delay

        change the interval to ``None`` or an ``int`` / ``float`` in seconds.
        If the delay is ``None``, the function will no longer fire.

    .. method:: clear(self)

        Equivalent to ``my_timeout.delay = None``
