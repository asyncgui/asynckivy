__all__ = ('sleep', 'sleep_free', 'sleep_forever', )

import types

from kivy.clock import Clock
schedule_once = Clock.schedule_once
def _raise_exception_for_free_type_clock_not_being_available(*args, **kwargs):
    raise Exception(
        "'Clock.schedule_once_free()' is not available."
        " Use a non-default clock."
    )
schedule_once_free = getattr(
    Clock, 'schedule_once_free',
    _raise_exception_for_free_type_clock_not_being_available
)


@types.coroutine
def sleep(duration):
    args, kwargs = yield \
        lambda step_coro: schedule_once(step_coro, duration)
    return args[0]


@types.coroutine
def sleep_free(duration):
    '''(experimental)'''
    args, kwargs = yield \
        lambda step_coro: schedule_once_free(step_coro, duration)
    return args[0]


@types.coroutine
def sleep_forever():
    yield lambda step_coro: None
