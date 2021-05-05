__all__ = ('sleep', 'sleep_free', 'create_sleep', )

import types

from kivy.clock import Clock
create_trigger = Clock.create_trigger
create_trigger_free = getattr(Clock, 'create_trigger_free', None)


@types.coroutine
def sleep(duration):
    args, kwargs = yield lambda step_coro: \
        create_trigger(step_coro, duration, release_ref=False)()
    return args[0]


@types.coroutine
def sleep_free(duration):
    '''(experimental)'''
    args, kwargs = yield lambda step_coro: \
        create_trigger_free(step_coro, duration, release_ref=False)()
    return args[0]


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
    clock_event = Clock.create_trigger(
        await get_step_coro(), duration, release_ref=False)

    @types.coroutine
    def sleep():
        return (yield clock_event)[0][0]
    return sleep
