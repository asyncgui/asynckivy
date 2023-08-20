__all__ = ('sleep', 'sleep_free', 'repeat_sleeping', )

import typing as T
import types
from functools import partial

from kivy.clock import Clock
from asyncgui import current_task, Cancelled, _sleep_forever


@types.coroutine
def sleep(duration) -> T.Awaitable[float]:
    '''
    The async form of :meth:`kivy.clock.Clock.schedule_once`.

    .. code-block::

        dt = await sleep(5)  # wait for 5 seconds
    '''
    clock_event = None

    def _sleep(task):
        nonlocal clock_event
        clock_event = Clock.create_trigger(task._step, duration, False, False)
        clock_event()

    try:
        return (yield _sleep)[0][0]
    except Cancelled:
        clock_event.cancel()
        raise


@types.coroutine
def sleep_free(duration) -> T.Awaitable[float]:
    '''
    The async form of :meth:`kivy.clock.Clock.schedule_once_free`.

    .. code-block::

        dt = await sleep_free(5)  # wait for 5 seconds
    '''
    clock_event = None

    def _sleep_free(task):
        nonlocal clock_event
        clock_event = Clock.create_trigger_free(task._step, duration, False, False)
        clock_event()

    try:
        return (yield _sleep_free)[0][0]
    except Cancelled:
        clock_event.cancel()
        raise


class repeat_sleeping:
    '''
    Return an async context manager that provides an efficient way to repeat sleeping.

    When there is code like this:

    .. code-block::

        while True:
            await sleep(0)
            ...

    it can be translated to:

    .. code-block::

        async with repeat_sleeping(step=0) as sleep:
            while True:
                await sleep()
                ...

    The latter is more efficient than the former because it only creates one :class:`kivy.clock.ClockEvent` instance
    and re-uses it during the loop while the former creates it per iteration.

    **Restriction**

    By default, you are not allowed to perform any kind of async operations inside the with-block except you can
    ``await`` the return value of the function that is bound to the identifier of the as-clause.

    .. code-block::

        async with repeat_sleeping(step=0) as sleep:
            await sleep()  # OK
            await something_else  # NOT ALLOWED
            async with async_context_manager:  # NOT ALLOWED
                ...
            async for __ in async_iterator:  # NOT ALLOWED
                ...

    If you wish to override that restriction, you can set the ``free_await`` parameter to True. However, please note
    that enabling ``free_await`` may result in a slight performance sacrifice.
    '''

    __slots__ = ('_step', '_free_await', '_trigger', )

    def __init__(self, *, step, free_await=False):
        self._step = step
        self._free_await = free_await

    async def __aenter__(self) -> T.Awaitable[T.Callable[[], T.Awaitable[float]]]:
        free = self._free_await
        self._trigger = trigger = Clock.create_trigger((await current_task())._step, self._step, not free, False)
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
