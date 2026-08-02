=====
Notes
=====

-----------------------------
Why this library even exists
-----------------------------

Starting from version 2.0.0, Kivy supports two legitimate async libraries: :mod:`asyncio` and :mod:`trio`.
At first glance, developing another one might seem like `reinventing the wheel`_.
Actually, I originally started this project just to learn how the async/await syntax works —
so at first, it really was 'reinventing the wheel'.

But after experimenting with Trio in combination with Kivy for a while,
I noticed that Trio isn't suitable for situations requiring fast reactions, such as handling touch events.
The same applies to asyncio.
You can confirm this by running ``investigation/why_xxx_is_not_suitable_for_handling_touch_events.py`` and rapidly clicking a mouse button.
You'll notice that sometimes ``'up'`` isn't paired with a corresponding ``'down'`` in the console output.
You'll also see that the touch coordinates aren't relative to a ``RelativeLayout``,
even though the widget receiving the touches belongs to it.

The cause of these problems is that :meth:`trio.Event.set` and :meth:`asyncio.Event.set` don't *immediately* resume the tasks waiting for the ``Event`` to be set —
they merely schedule them to resume.
The same is true for :meth:`trio.Nursery.start_soon` and :func:`asyncio.create_task`.

Trio and asyncio are async **I/O** libraries after all.
They probably don't need to resume or start tasks immediately, but I believe this is essential for touch handling in Kivy.
If touch events aren't processed promptly, their state might change before tasks even have a chance to handle them.
Their core design might not be ideal for GUI applications in the first place.
That's why I continue to develop the asynckivy library to this day.

Edit:
Python 3.14 introduced a ``eager_start`` parameter for :func:`asyncio.create_task` and :meth:`asyncio.TaskGroup.create_task`.
There is also a discussion about `immediate resumption`_.
So, it is possible that asyncio will eventually support all the capabilities provided by asynckivy.

.. _immediate resumption: https://discuss.python.org/t/an-eager-way-to-set-result-on-asyncio-future/106161
.. _reinventing the wheel: https://en.wikipedia.org/wiki/Reinventing_the_wheel

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
        interact with Kivy except through ``Clock``.
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

Because of this, you have to explicitly close async generators when you're done with them if either library is running.
The following ones are affected:

- :func:`~asynckivy.interpolate`
- :func:`~asynckivy.interpolate_seq`
- :func:`~asynckivy.anim_with_ratio`

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
Therefore, do **not** perform any async operations while consuming an async generator.

.. code-block::

    async for __ in async_generator:
        await awaitable  # Don't
        async with async_context_manager:  # Don't
            ...
        async for __ in async_iterator:  # Don't
            ...
