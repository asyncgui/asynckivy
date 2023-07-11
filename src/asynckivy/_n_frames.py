__all__ = ('n_frames', 'one_frame', )

import typing as T
import types
from kivy.clock import Clock

_waiting_tasks = []


def _resume(dt):
    global _waiting_tasks
    tasks = _waiting_tasks
    _waiting_tasks = []
    for t in tasks:
        if t is not None:
            t._step()


# NOTE: This hinders the 'kivy_clock'-fixture
_trigger_resume = Clock.create_trigger(_resume, 0)


@types.coroutine
def one_frame() -> T.Awaitable:
    '''
    Wait for one frame.

    .. code-block::

        await ak.one_frame()
    '''
    _trigger_resume()
    tasks = _waiting_tasks
    idx = len(tasks)
    try:
        yield tasks.append
    finally:
        tasks[idx] = None


async def n_frames(n: int) -> T.Awaitable:
    '''
    Wait for the specified number of frames.

    .. code-block::

        await n_frames(2)
    '''
    if n < 0:
        raise ValueError("Cannot wait for negative number of frames")
    _one_frame = one_frame
    for __ in range(n):
        await _one_frame()
