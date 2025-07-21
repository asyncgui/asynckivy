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

Because of this, you have to explicitly close asynckivy-flavored async generators when you're done with them.
Here are the affected ones:

- :func:`~asynckivy.rest_of_touch_events`
- :func:`~asynckivy.interpolate`
- :func:`~asynckivy.interpolate_seq`
- ``anim_with_xxx``

An alternative is to avoid using an async generator by copying and pasting the internal logic of these functions.
For example, suppose you're using ``anim_with_et``, and the code around it doesn't behave as expected:

.. code-block::

    async for et in anim_with_et(...):
        ...

You can refer to its source code and replace the above with its internal logic:

.. code-block::

    with sleep_freq(...) as sleep:
        et = 0.
        while True:
            dt = await sleep()
            et += dt
            ...

Many of you may think this is a stupid idea, but this is sometimes worth it.
Async generators are fragile enough to justify such workarounds.

----------------------------------------------
Places where async operations were disallowed
----------------------------------------------

Until version 0.8.x, many APIs that return async generators did not allow async operations during iteration.

- :func:`~asynckivy.interpolate`
- :func:`~asynckivy.interpolate_seq`
- ``anim_with_xxx``

.. code-block::

    async for v in interpolate(...):
        await awaitable  # NOT ALLOWED
        async with async_context_manager:  # NOT ALLOWED
            ...
        async for v in async_iterator:  # NOT ALLOWED
            ...

As of version 0.9.0, these restrictions have been lifted.  
Only :func:`~asynckivy.rest_of_touch_events` still disallows async operations during iteration.
