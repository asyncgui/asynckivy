__all__ = ('wait_for_a_frame', )

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
def wait_for_a_frame():
    '''(internal)'''
    _trigger_resume()
    yield _waiting.append
