from contextlib import AbstractAsyncContextManager

from kivy.clock import Clock
from asyncgui import move_on_when, Task, ExclusiveEvent


def sleep(duration):
    '''
    An async form of :meth:`kivy.clock.Clock.schedule_once`.

    .. code-block::

        dt = await sleep(5)  # wait for 5 seconds
    '''
    e = ExclusiveEvent()
    clock_event = Clock.create_trigger(e.fire, duration, False, False)
    clock_event()
    return e.wait_args_0()


def sleep_free(duration):
    '''
    An async form of :meth:`kivy.clock.Clock.schedule_once_free`.

    .. code-block::

        dt = await sleep_free(5)  # wait for 5 seconds
    '''
    e = ExclusiveEvent()
    clock_event = Clock.create_trigger_free(e.fire, duration, False, False)
    clock_event()
    return e.wait_args_0()


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

        with sleep_freq(0.1) as sleep:
            while True:
                dt = await sleep()
                print(dt)
                if some_condition:
                    break

    .. versionchanged:: 0.9.0

        * The API was made public again.
        * The ``free_to_await`` parameter was added.

    .. versionchanged:: 0.11.0

        * This can be used as either a synchronous or an asynchronous context manager.
          Prefer the synchronous form, as it has less overhead.
        * The ``free_to_await`` parameter was removed. You can treat it as if it were always set to True.
    '''

    __slots__ = ("_step", "_trigger", )

    def __init__(self, step=0):
        self._step = step

    def __enter__(self):
        e = ExclusiveEvent()
        self._trigger = t = Clock.create_trigger(e.fire, self._step, True, False)
        t()
        return e.wait_args_0

    def __exit__(self, *args):
        self._trigger.cancel()

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, *args):
        return self.__exit__(*args)


async def anim_with_ratio(*, base, step=0):
    '''
    Returns an async iterator that yields the elapsed time since the start of the iteration, divided by ``base``.

    .. code-block::

        async for p in anim_with_ratio(base=3):
            print(p)

    The code above is equivalent to the following:

    .. code-block::

        with sleep_freq() as sleep:
            base = 3
            total_elapsed_time = 0.
            while True:
                total_elapsed_time += await sleep()
                p = total_elapsed_time / base
                print(p)

    Use :class:`kivy.animation.AnimationTransition` for non-linear curves.

    .. code-block::

        from kivy.animation import AnimationTransition

        in_cubic = AnimationTransition.in_cubic

        async for p in anim_with_ratio(base=...):
            p = in_cubic(p)
            print(p)

    .. versionadded:: 0.6.1

    .. versionchanged:: 0.7.0

        The ``duration`` parameter was replaced with ``base``.
        The loop no longer ends on its own.
    '''
    with sleep_freq(step=step) as sleep:
        et = 0.
        while True:
            et += await sleep()
            yield et / base


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


async def n_frames(n: int):
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

    e = ExclusiveEvent()

    def callback(dt):
        nonlocal n
        n -= 1
        if not n:
            e.fire()
            return False

    clock_event = Clock.schedule_interval(callback, 0)

    try:
        await e.wait()
    finally:
        clock_event.cancel()
