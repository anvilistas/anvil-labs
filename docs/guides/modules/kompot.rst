Kompot
======

Kompot exposes a serialization mechanism for Python builtins and Anvil portable classes.

Kompot provides wrappers for ``anvil.server.call()`` and ``@anvil.server.callable`` to take advantage of
the enhanced serialization between client and server calls.


Wikipedia on kompot:

    In 1885, Lucyna Ćwierczakiewiczowa wrote in a recipe book that
    **kompot** preserved fruit so well it seemed fresh


Builtins
--------
In addition to standard JSONable types, kompot supports the following builtins:

``set``, ``frozenset``, ``tuple``, ``date``, ``datetime``

``dict`` objects will preserve their order and keys can be arbitrary.

``type`` objects registered with kompot can also be serialized.



API
---

.. function:: register(cls)

    All portable classes that kompot can serialize must be registered by calling ``register(cls)``.

    .. code-block:: python

        from anvil_labs import kompot
        import anvil.server

        @anvil.server.portable_class
        class Foo:
            ...

        kompot.register(Foo)

    *(kompot.register can also be used as a decorator)*


.. function:: serialize(obj)

    Serialize an arbitrary object into a JSONable object.

    If kompot does not know how to handle the object, it will be left untouched.

    Kompot does not know how to handle objects like:

        - anvil table rows
        - media objects
        - capabilities

    We leave Anvil to serialize these objects when calling the server.

.. function:: preserve(obj)

    Like ``serialize`` but will throw a ``SerializationError`` if there are any unhandled objects.

    Use ``preserve`` for storing an object as a simple object.

    Use ``serialize`` for sending an object from the client to the server.


.. function:: reconstruct(obj)

    Reconstruct an object from the output of ``serialize`` or ``preserve``

.. function:: call(fn_name, *args, **kws)
              call_s(fn_name, *args, **kws)
              call_async(fn_name, *args, **kws)

    Use inplace of ``anvil.server.call()``

    Kompot will serialize the args and kws and reconstruct the returned value.

    The server function must be decorated with ``@kompot.callable``.


.. decorator:: callable

    Use inplace of ``@anvil.server.callable``.

    Kompot will reconstruct the serialized args and kws,
    call the original function and then serialize the return value.

    Must be combined with ``kompot.call()``.
