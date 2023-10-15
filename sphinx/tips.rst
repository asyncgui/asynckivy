====
Tips
====

.. _io-in-asynckivy:

---------------
IO in AsyncKivy
---------------

``asynckivy`` does not have any I/O primitives like ``trio`` and ``asyncio`` do,
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

Unhandled :exc:`Exception` (not :exc:`BaseException`) is propagated to the caller so you can catch it like you do in
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

(under construction)
