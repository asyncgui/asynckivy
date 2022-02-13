'''
notes for maintainers
---------------------

default引数を使ってLOAD_GLOBALをLAOD_FASTに変えている箇所がありますがコードが読みにくくなる悪手かもしれない。
'''
__all__ = ('n_frames', 'one_frame', )

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
def one_frame(*, _trigger_resume=_trigger_resume):
    '''(experimental)
    wait for one frame.

    Usage
    -----

    .. code-block:: python

       import asynckivy as ak

       async def async_fn():
           await ak.one_frame()
    '''
    _trigger_resume()
    yield _waiting.append


async def n_frames(n: int, *, _one_frame=one_frame, _range=range):
    '''(experimental)
    wait for the specified number of frames.

    Usage
    -----

    .. code-block:: python

       import asynckivy as ak

       async def async_fn():
           await ak.n_frames(2)  # wait for two frames
    '''
    if n < 0:
        raise ValueError("Cannot wait for negative number of frames")
    for __ in _range(n):
        await _one_frame()
