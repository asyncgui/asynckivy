__all__ = ("sleep", "sleep_free", "repeat_sleeping", "move_on_after", "n_frames", )

from contextlib import AbstractAsyncContextManager
import types

from kivy.clock import Clock
from asyncgui import _current_task, _sleep_forever, move_on_when, Task, Cancelled, ExclusiveEvent


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


class repeat_sleeping:
    '''
    (internal)
    Returns a context manager that provides an efficient way to repeat sleeping.

    When there is a piece of code like this:

    .. code-block::

        while True:
            await sleep(0)
            ...

    it can be translated to:

    .. code-block::

        with repeat_sleeping(step=0) as sleep:
            while True:
                await sleep()
                ...

    The latter is more suitable for situations requiring frequent sleeps, such as moving an object in every frame.

    .. versionchanged:: 0.8.0

        This API is now private.

    .. versionchanged:: 0.9.0

        The API now returns a regular (non-async) context manager.
        Async operations are allowed within the context block.

        .. code-block::

            with repeat_sleeping() as sleep:
                await sleep()  # OK
                await something_else  # OK
    '''

    __slots__ = ('_step', '_trigger', )

    def __init__(self, *, step=0):
        self._step = step

    def __enter__(self):
        e = ExclusiveEvent()
        self._trigger = t = Clock.create_trigger(e.fire, self._step, True, False)
        t()
        return e.wait_first_arg

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._trigger.cancel()


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
