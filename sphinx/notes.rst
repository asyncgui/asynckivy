=====
Notes
=====

.. _io-in-asynckivy:

----------------
I/O in AsyncKivy
----------------

``asynckivy`` does not have any I/O primitives unlike ``trio`` and ``asyncio`` do,
thus threads may be the best way to perform them without blocking the main-thread:

.. code-block::

    from concurrent.futures import ThreadPoolExecutor
    import asynckivy as ak

    executor = ThreadPoolExecutor()


    def thread_blocking_operation():
        '''
        This function is called from outside the main-thread so you should not
        perform any graphics-related operations here.
        '''


    async def async_fn():
        r = await ak.run_in_thread(thread_blocking_operation)
        print("return value:", r)

        r = await ak.run_in_executor(executor, thread_blocking_operation)
        print("return value:", r)

Unhandled exceptions (not :exc:`BaseException`) are propagated to the caller so you can catch them like you do in
synchronous code:

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
which likely hinders asynckivy-flavored async generators.
You can see its details `here <https://peps.python.org/pep-0525/#finalization>`__.

Because of that, the APIs that create async generators might not work perfectly if ``asyncio`` or ``trio`` is running.
Here is a list of them:

- :func:`asynckivy.rest_of_touch_events`
- :func:`asynckivy.interpolate`
- :func:`asynckivy.interpolate_seq`
- :func:`asynckivy.fade_transition`
- ``asynckivy.anim_with_xxx``


--------------------------------------------------------
Places where async operations were previously disallowed
--------------------------------------------------------

Most asynckivy APIs that return an async iterator don't allow async operations during iteration.
Here is a list of them:

- :func:`asynckivy.rest_of_touch_events`
- :func:`asynckivy.interpolate`
- :func:`asynckivy.interpolate_seq`
- ``asynckivy.anim_with_xxx``
- :any:`asynckivy.event_freq`

.. code-block::

    async for __ in rest_of_touch_events(...):
        await awaitable  # NOT ALLOWED
        async with async_context_manager:  # NOT ALLOWED
            ...
        async for __ in async_iterator:  # NOT ALLOWED
            ...
