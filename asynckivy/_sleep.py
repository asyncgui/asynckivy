__all__ = ('sleep', 'sleep_forever', )

import types

from kivy.clock import Clock
Clock_schedule_once = Clock.schedule_once


@types.coroutine
def sleep(duration):
    args, kwargs = yield \
        lambda step_coro: Clock_schedule_once(step_coro, duration)
    return args[0]


@types.coroutine
def sleep_forever():
    yield lambda step_coro: None
