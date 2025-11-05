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
Therefore, do **not** perform any async operations while consuming the async generators returned by the APIs listed above.

.. code-block::

    async for __ in rest_of_touch_events(...):
        await awaitable  # NOT ALLOWED
        async with async_context_manager:  # NOT ALLOWED
            ...
        async for __ in async_iterator:  # NOT ALLOWED
            ...

If you really need to perform async operations while consuming those async generators,
consider using :class:`~asynckivy.rest_of_touch_events_cm` or :class:`~asynckivy.sleep_freq` instead.
They make your code more verbose, but they free you from having to deal with the problems, since they don't rely on async generators at all.

.. code-block::
    
    async with rest_of_touch_events_cm(..., free_to_await=True) as on_touch_move:
        ...

    async with sleep_freq(..., free_to_await=True) as sleep:
        ...
