__all__ = ('n_frames', )

import typing as T
import types
from kivy.clock import Clock
from asyncgui import _current_task, _sleep_forever


@types.coroutine
def n_frames(n: int) -> T.Awaitable:
    '''
    Waits for a specified number of frames.

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
