__all__ = ('n_frames', )

import types
from kivy.clock import Clock

_waiting = []


def _resume(dt):
    global _waiting
    waiting = _waiting
    _waiting = []
    for step_coro in waiting:
        step_coro()


# NOTE: This hinders the 'kivy_clock'-fixture
_trigger_resume = Clock.create_trigger(_resume, 0)


@types.coroutine
def _wait_for_a_frame():
    '''(internal)'''
    _trigger_resume()
    yield _waiting.append


async def n_frames(n: int):
    '''(experimental)
    wait for the specified number of frames.

    Usage
    -----

    .. code-block:: python

       import asynckivy as ak

       async def async_fn():
           await ak.n_frames(2)  # wait for two frames
    '''
    wait_for_a_frame = _wait_for_a_frame
    if n < 0:
        raise ValueError("Cannot wait for negative number of frames")
    for __ in range(n):
        await wait_for_a_frame()
