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

    from anvil_labs.non_blocking import call_async

    def button_click(self, **event_args):
        self.update_database()
        self.open_form("Form1")

    def update_database(self):
        # Unlike anvil.server.call we do not wait for the call to return
        call_async("update", self.item)


If you care about the return value, you can provide handlers.

.. code-block:: python

    from anvil_labs.non_blocking import call_async

    def handle_result(self, res):
        print(res)
        Notification("successfully saved").show()

    def handle_error(self, err):
        print(err)
        Notification("there was a problem", style="danger").show()

    def update_database(self, **event_args):
        call_async("update", self.item).on_result(self.handle_result, self.handle_error)
        # Equivalent to
        async_call = call_async("update", self.item)
        async_call.on_result(self.handle_result, self.handle_error)
        # Equivalent to
        async_call = call_async("update", self.item)
        async_call.on_result(self.handle_result)
        async_call.on_error(self.handle_error)


repeat
******

Call a function repeatedly using the ``repeat()`` function.
After each interval seconds the function will be called.
To end or cancel the repeated call use the ``cancel`` method.


.. code-block:: python

    from anvil_labs import non_blocking

    i = 0
    def do_heartbeat():
        global heartbeat, i
        if i >= 42:
            heartbeat.cancel()
            # equivalent to non_blocking.cancel(heartbeat)
        print("da dum")
        i += 1

    heartbeat = non_blocking.repeat(do_heartbeat, 1)


delay
*****

Call a function after a timeout using the ``delay()`` function.
After the timeout is reached the function will be called.
To ``cancel`` the delayed call, use the ``cancel()`` method.

.. code-block:: python

    from anvil_labs import non_blocking

    pending = []

    def do_save():
        global pending
        pending, saves = [], pending
        if not saves:
            return
        anvil.server.call_s("save", saves)

    save_timeout = None

    def on_save(saves):
        global pending, save_timeout
        non_blocking.cancel(save_timeout)
        # we could also use save_timeout.cancel() but we start with None
        pending.extend(saves)
        save_timeout = non_blocking.delay(do_save, 1)

    # calling on_save() repeatedly will cancel the current do_save delayed call and create a new one


API
---

.. function:: call_async(fn, *args, **kws)
              call_async(fn_name, *args, **kws)

    Returns an ``AyncCall`` object. The *fn* will be called in a non-blocking way.

    If the first argument is a string then the server function with name *fn_name* will be called in a non-blocking way.

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
