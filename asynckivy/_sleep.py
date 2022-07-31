__all__ = ('sleep', 'sleep_free', 'create_sleep', 'repeat_sleeping', )

import types
from functools import partial

from kivy.clock import Clock
from asyncgui import get_step_coro

# NOTE: This hinders the 'kivy_clock'-fixture
create_trigger = Clock.create_trigger
create_trigger_free = getattr(Clock, 'create_trigger_free', None)


@types.coroutine
def sleep(duration):
    args, kwargs = yield lambda step_coro, _d=duration: create_trigger(step_coro, _d, False, False)()
    return args[0]


@types.coroutine
def sleep_free(duration):
    '''(experimental)'''
    args, kwargs = yield lambda step_coro, _d=duration: create_trigger_free(step_coro, _d, False, False)()
    return args[0]


class repeat_sleeping:
    '''(experimental)
    Return an async context manager that provides an efficient way to repeat sleeping. When there is code like this:

    .. code-block:: python

        while True:
            await asynckivy.sleep(2)

    it can be translated into this:

    .. code-block:: python

        async with asynckivy.repeat_sleeping(2) as sleep:
            while True:
                await sleep()

    which is more efficient. The reason of it is that the latter only creates one ``ClockEvent``, and re-uses it
    during the loop as opposed to the former, which creates a ``ClockEvent`` in every iteration.

    Restriction
    -----------

    By default, the only thing you can 'await' during the context manager is the sleep returned by it. If you want to
    'await' something else, you need to set ``free_await`` to True.

    .. code-block:: python

        async with asynckivy.repeat_sleeping(2, free_await=True) as sleep:
            await something_else
            while True:
                await sleep()
                await something_else
    '''

    __slots__ = ('_step', '_free_await', '_trigger', )

    @types.coroutine
    def sleep(f):
        return (yield f)[0][0]

    def __init__(self, step, free_await=False):
        self._step = step
        self._free_await = free_await

    async def __aenter__(
            self, partial=partial, create_trigger=create_trigger, sleep=sleep, get_step_coro=get_step_coro,
            do_nothing=lambda step_coro: None):
        free = self._free_await
        self._trigger = trigger = create_trigger(await get_step_coro(), self._step, not free, False)
        trigger()
        return partial(sleep, trigger if free else do_nothing)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._trigger.cancel()


async def create_sleep(duration):
    '''(internal) Improves the performance by re-using a ClockEvent.

        sleep_for_1sec = await create_sleep(1)
        while True:
            dt = await sleep_for_1sec()
            # do whatever you want

    WARNING:

        In the example above, "sleep_for_1sec" must be awaited in the same
        async-thread that created it. That means the following code is not
        allowed:

            sleep_for_1sec = await create_sleep(1)

            asynckivy.start(sleep_for_1sec())  # No
            asynckivy.and_(sleep_for_1sec(), ...)  # No
            asynckivy.or_(sleep_for_1sec(), ...)  # No

            async def some_fn():
                await sleep_for_1sec()
            asynckivy.start(some_fn())  # No

        But the following code is allowed:

            sleep_for_1sec = await create_sleep(1)

            async def some_fn():
                await sleep_for_1sec()
            await some_fn()  # OK
    '''
    from asyncgui import get_step_coro
    clock_event = Clock.create_trigger(await get_step_coro(), duration, False, False)

    @types.coroutine
    def sleep():
        return (yield clock_event)[0][0]
    return sleep
