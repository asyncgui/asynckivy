__all__ = ('sleep', 'sleep_free', 'repeat_sleeping', )

import types
from functools import partial

from kivy.clock import Clock
from asyncgui import current_task, Cancelled, sleep_forever

_sleep_forever = sleep_forever.__defaults__[0]
# NOTE: This hinders the 'kivy_clock'-fixture
create_trigger = Clock.create_trigger
create_trigger_free = getattr(Clock, 'create_trigger_free', None)


@types.coroutine
def sleep(duration):
    clock_event = None

    def _sleep(task):
        nonlocal clock_event
        clock_event = create_trigger(task._step, duration, False, False)
        clock_event()

    try:
        return (yield _sleep)[0][0]
    except Cancelled:
        clock_event.cancel()
        raise


@types.coroutine
def sleep_free(duration):
    clock_event = None

    def _sleep_free(task):
        nonlocal clock_event
        clock_event = create_trigger_free(task._step, duration, False, False)
        clock_event()

    try:
        return (yield _sleep_free)[0][0]
    except Cancelled:
        clock_event.cancel()
        raise


class repeat_sleeping:
    '''
    Return an async context manager that provides an efficient way to repeat sleeping.

    The following code:

    .. code-block::

        while True:
            await asynckivy.sleep(0)

    can be translated to:

    .. code-block::

        async with asynckivy.repeat_sleeping(0) as sleep:
            while True:
                await sleep()

    The latter is more efficient than the former. The reason is that the latter only creates one ``ClockEvent``
    instance while the former creates it per iteration.

    By default, you are not allowed to perform any kind of async operations inside the with-block except you can
    ``await`` the return value of the function that is bound to the identifier of the as-clause.

    .. code-block::

        async with asynckivy.repeat_sleeping(0) as sleep:
            await sleep()  # OK
            await something_else  # NOT ALLOWED
            async with async_context_manager:  # NOT ALLOWED
                ...
            async for __ in async_iterable:  # NOT ALLOWED
                ...

    If you wish to override that restriction, you can set the ``free_await`` parameter to True. However, please note
    that enabling ``free_await`` may result in a slight performance sacrifice.
    '''

    __slots__ = ('_step', '_free_await', '_trigger', )

    def __init__(self, step, free_await=False):
        self._step = step
        self._free_await = free_await

    async def __aenter__(self):
        free = self._free_await
        self._trigger = trigger = create_trigger((await current_task())._step, self._step, not free, False)
        if free:
            return partial(_efficient_sleep_ver_flexible, trigger)
        else:
            trigger()
            return _efficient_sleep_ver_fast

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._trigger.cancel()


@types.coroutine
def _efficient_sleep_ver_fast(_f=_sleep_forever):
    return (yield _f)[0][0]


@types.coroutine
def _efficient_sleep_ver_flexible(f):
    try:
        return (yield f)[0][0]
    except Cancelled:
        f.cancel()
        raise
