=====
Notes
=====

.. _io-in-asynckivy:

----------------
I/O in AsyncKivy
----------------

Unlike ``trio`` and ``asyncio``, ``asynckivy`` does not provide any I/O primitives.  
Therefore, if you don't want to implement your own, using threads may be the best way to perform
I/O without blocking the main thread.

.. code-block::

    from concurrent.futures import ThreadPoolExecutor
    import asynckivy as ak

    executor = ThreadPoolExecutor()


    def thread_blocking_operation():
        '''
        This function is called from outside the main thread so you should not
        perform any graphics-related operations here.
        '''


    async def async_fn():
        r = await ak.run_in_thread(thread_blocking_operation)
        print("return value:", r)

        r = await ak.run_in_executor(executor, thread_blocking_operation)
        print("return value:", r)

Unhandled exceptions (excluding :exc:`BaseException` that is not :exc:`Exception`) are propagated
to the caller so you can catch them like you do in synchronous code:

.. code-block::

    import requests
    import asynckivy as ak

    async def async_fn(label):
        try:
            response = await ak.run_in_thread(lambda: requests.get('htt...', timeout=10))
        except requests.Timeout:
            label.text = "TIMEOUT!"
        else:
            label.text = "RECEIVED"

.. _kivys-event-system:

-------------------
Kivy's Event System
-------------------

(under construction)


.. The stop_dispatching can be used to prevent the execution of callbacks (and the default handler) bound to
.. the event.
.. (Though not the all callbacks, but the ones that are bound to the event **before** the call to :func:`event`.)

.. .. code-block::

..     button.bind(on_press=lambda __: print("callback 1"))
..     button.bind(on_press=lambda __: print("callback 2"))

..     # Wait for a button to be pressed. When that happend, the above callbacks won't be called because they were
..     # bound before the execution of ``await event(...)``.
..     await event(button, 'on_press', stop_dispatching=True)

.. You may feel weired

.. .. code-block::

..     # Wait for an ``on_touch_down`` event to occur inside a widget. When that happend, the event 
..     await event(
..         widget, 'on_touch_down', stop_dispatching=True,
..         filter=lambda w, t: w.collide_point(*t.opos),
..     )

.. _the-problem-with-async-generators:

---------------------------------
The Problem with Async Generators
---------------------------------

:mod:`asyncio` and :mod:`trio` do some hacky stuff, :func:`sys.set_asyncgen_hooks` and :func:`sys.get_asyncgen_hooks`,
which sometimes delays the cleanup of async generators when either library is running.
You can read more about this in `PEP 525 <https://peps.python.org/pep-0525/#finalization>`__.

Because of this, you have to explicitly close async generators when you're done with them.
The following ones are affected:

- :func:`~asynckivy.rest_of_touch_events`
- :func:`~asynckivy.interpolate`
- :func:`~asynckivy.interpolate_seq`
- ``anim_with_xxx``

.. code-block::

    from contextlib import aclosing

    async with aclosing(interpolate(...)) as agen:
        async for v in agen:
            ...

And there's another problem, and this one isn't tied to ``asyncio`` or ``trio``.
If an exception occurs on the *consumer side* of an async generator, the exception is **not** propagated to the generator.
(This also applies to regular generators, but it's generally less of a concern there.)

.. code-block::

    async for v in agen:
        # If an exception occurs here, it won't be propagated to the agen.

This means that if the consumer is cancelled, the exception representing that cancellation won't reach the generator.

.. code-block::

    async for v in agen:
        await something  # If cancelled here, the agen won't be able to respond to it correctly depending on how it's implemented.

I won't go into the details here — it's complicated — but in short, this behavior can break ``asyncgui``'s cancellation system.
I'm currently working on a possible fix here: https://github.com/asyncgui/asyncgui/pull/136 — but I'm not sure whether it will work.

**So here's my suggestion for now:**
If something goes wrong with an async generator, just abandon it and copy-paste its internal logic instead.
A prime example of this can be seen in ``painter3.py`` vs ``painter4.py`` in the examples directory.
I know this may sound like a terrible idea, but async generators are problematic enough to justify such workarounds.

--------------------------------------------
Places where async operations are disallowed
--------------------------------------------

Most asynckivy APIs that return an async iterator don't allow async operations during iteration.
Here is a list of them:

- :func:`~asynckivy.rest_of_touch_events`
- :func:`~asynckivy.interpolate`
- :func:`~asynckivy.interpolate_seq`
- ``anim_with_xxx``

.. code-block::

    async for __ in rest_of_touch_events(...):
        await awaitable  # NOT ALLOWED
        async with async_context_manager:  # NOT ALLOWED
            ...
        async for __ in async_iterator:  # NOT ALLOWED
            ...
