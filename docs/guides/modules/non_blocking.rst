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
        _ = call_server_async("update", self.item)
        _.on_result(self.handle_result, self.handle_result)
        # Equivalent to
        _ = call_server_async("update", self.item)
        _.on_result(self.handle_result)
        _.on_error(self.handle_error)


Interval
********

Create a Timer-like object in code without worrying about components.

.. code-block:: python

    from anvil_labs.non_blocking import Interval

    i = 0
    def do_heartbeat():
        global heartbeat, i
        if i >= 100:
            heartbeat.interval = 0
        print("da dum")
        i += 1

    heartbeat = Interval(do_heartbeat, 1)




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

    .. method:: wait(self)

        Waits for the non-blocking call to finish executing and returns the result.


.. class:: Interval(fn, interval=None)

    Create an interval that will call a function every delay seconds.
    If the delay is ``0`` or ``None`` the Interval will stop calling the function.

    .. attribute:: interval

        change the interval to ``None`` or an ``int`` / ``float`` in seconds.
        If the interval is ``None`` or ``0``, the function will no longer fire.

    .. method:: clear_interval(self)

        Equivalent to ``my_interval.interval = None``
