__all__ = ("sleep", "sleep_free", "repeat_sleeping", "move_on_after", "n_frames", "sleep_freq", )

from contextlib import AbstractAsyncContextManager
import types

from kivy.clock import Clock
from asyncgui import _current_task, _sleep_forever, move_on_when, Task, Cancelled, ExclusiveEvent, _wait_args_0


@types.coroutine
def sleep(duration):
    '''
    An async form of :meth:`kivy.clock.Clock.schedule_once`.

    .. code-block::

        dt = await sleep(5)  # wait for 5 seconds
    '''
    task = (yield _current_task)[0][0]
    clock_event = Clock.create_trigger(task._step, duration, False, False)
    clock_event()

    try:
        return (yield _sleep_forever)[0][0]
    except Cancelled:
        clock_event.cancel()
        raise


@types.coroutine
def sleep_free(duration):
    '''
    An async form of :meth:`kivy.clock.Clock.schedule_once_free`.

    .. code-block::

        dt = await sleep_free(5)  # wait for 5 seconds
    '''
    task = (yield _current_task)[0][0]
    clock_event = Clock.create_trigger_free(task._step, duration, False, False)
    clock_event()

    try:
        return (yield _sleep_forever)[0][0]
    except Cancelled:
        clock_event.cancel()
        raise


class sleep_freq:
    '''
    An async form of :meth:`kivy.clock.Clock.schedule_interval`. The following callback-style code:

    .. code-block::

        def callback(dt):
            print(dt)
            if some_condition:
                return False

        Clock.schedule_interval(callback, 0.1)

    is equivalent to the following async-style code:

    .. code-block::

        async with sleep_freq(0.1) as sleep:
            while True:
                dt = await sleep()
                print(dt)
                if some_condition:
                    break

    .. versionchanged:: 0.8.0
        The API was made private.

    .. versionchanged:: 0.9.0

        * The API was made public again.
        * The API was renamed from ``repeat_sleeping`` to ``sleep_freq``; the old name remains available as an alias.
        * The ``free_to_await`` parameter was added.

    The ``free_to_await`` parameter:

    If set to False (the default), the only permitted async operation within the with-block is ``await xxx()``,
    where ``xxx`` is the identifier specified in the as-clause. To lift this restriction, set ``free_to_await`` to
    True — at the cost of slightly reduced performance.
    '''

    __slots__ = ('_step', '_trigger', '_free_to_await')

    def __init__(self, step=0, free_to_await=False):
        self._step = step
        self._free_to_await = free_to_await

    @types.coroutine
    def __aenter__(self):
        if self._free_to_await:
            e = ExclusiveEvent()
            self._trigger = t = Clock.create_trigger(e.fire, self._step, True, False)
            t()
            return e.wait_args_0
        else:
            task = (yield _current_task)[0][0]
            self._trigger = t = Clock.create_trigger(task._step, self._step, True, False)
            t()
            return _wait_args_0

    async def __aexit__(self, *args):
        self._trigger.cancel()


repeat_sleeping = sleep_freq
'''An alias of :class:`sleep_freq`.'''


def move_on_after(seconds: float) -> AbstractAsyncContextManager[Task]:
    '''
    Returns an async context manager that applies a time limit to its code block,
    like :func:`trio.move_on_after` does.

    .. code-block::

        async with move_on_after(seconds) as timeout_tracker:
            ...
        if timeout_tracker.finished:
            print("The code block was interrupted due to a timeout")
        else:
            print("The code block exited gracefully.")

    .. versionadded:: 0.6.1
    '''
    return move_on_when(sleep(seconds))


@types.coroutine
def n_frames(n: int):
    '''
    Waits for a specified number of frames to elapse.

    .. code-block::

        await n_frames(2)

    If you want to wait for one frame, :func:`asynckivy.sleep` is preferable for a performance reason.

    .. code-block::

        await sleep(0)
    '''
    if n < 0:
        raise ValueError(f"Waiting for {n} frames doesn't make sense.")
    if not n:
        return

    task = (yield _current_task)[0][0]

    def callback(dt):
        nonlocal n
        n -= 1
        if not n:
            task._step()
            return False

    clock_event = Clock.schedule_interval(callback, 0)

    try:
        yield _sleep_forever
    finally:
        clock_event.cancel()
