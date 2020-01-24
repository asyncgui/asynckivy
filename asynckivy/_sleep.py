__all__ = ('sleep', 'sleep_forever', )

import types
from functools import partial

from kivy.clock import Clock
Clock_schedule_once = Clock.schedule_once


@types.coroutine
def sleep(duration):
    # The partial() here looks meaningless. But this is needed in order
    # to avoid weak reference
    args, kwargs = yield lambda step_coro: Clock_schedule_once(
        partial(step_coro), duration)
    return args[0]


@types.coroutine
def sleep_forever():
    yield lambda step_coro: None
