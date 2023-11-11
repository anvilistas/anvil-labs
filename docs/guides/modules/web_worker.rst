WebWorker
=========

The ``web_worker`` module supports creating client-side background tasks.

It is a limited API and should only be used for computational heavy calcuations on the client.
If you're doing something on the client that seems to be making the page unresponsive,
then a web worker might be for you.


You will need to include the following script tags in your Native Libraries for this module to work:

.. code-block:: python

    <script src="_/theme/anvil-labs/worker.js" defer></script>


Example
-------

Create a worker module - say ``fib_worker``

.. code-block:: python

    def fib(num):
        a, b = 1, 0
        i = 0
        print(worker) # worker is a global object injected into worker module
        while i < num:
            a, b = a + b, a
            i += 1
            worker.task_state["i"] = i
        return b


In your code use the ``web_worker`` module call the ``fib`` function as a background client side task

.. code-block:: python

    from anvil_labs.web_worker import Worker

    my_worker = Worker("fib_worker")

    class Form1(Form1Template):
        def fib_result(self, result):
            alert(result)

        def fib_error(self, error):
            raise error

        def timer_tick(self, state):
            if self.task.is_completed():
                self.timer.interval = 0
            else:
                print(self.task.get_state().get("i"))

        def button_1_click(self, **event_args):
            self.task = my_worker.launch_task("fib", 2**20)
            self.timer.interval = 1
            self.task.on_result(self.fib_result)
            self.task.on_error(self.fib_error)
            # self.task.on_state_change(self.fib_state_change)

Notes
-----

A worker module, like ``fib_worker`` above, can only import libraries from python's standard lib.

Exceptions raised should be from the standard lib.

Only JSONable objects can be passed to and from the worker to the client.

A Worker object can only launch a single background task at any one time.
You can create more Worker objects if you want multiple tasks to run in parallel.

The API for client side ``web_worker`` matches Anvil's API for launching and communicating with background tasks.
Using a Timer to check the current state of the web worker task will work in the same way.

There are 3 additions to the api - ``task.on_result()``, ``task.on_error()``, ``task.on_state_change()``.
You should pass a callback to these methods that can be used to receive information from the task object.
