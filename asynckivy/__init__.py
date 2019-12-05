__version__ = '0.0.2'
__all__ = ('start', 'sleep', 'event', )

import types
from functools import partial
from kivy.clock import Clock
from inspect import getcoroutinestate, CORO_CLOSED


def start(coro):
    def step_coro(*args, **kwargs):
        try:
            if getcoroutinestate(coro) != CORO_CLOSED:
                coro.send((args, kwargs, ))(step_coro)
        except StopIteration:
            pass

    try:
        coro.send(None)(step_coro)
    except StopIteration:
        pass


@types.coroutine
def sleep(duration):
    # The partial() here looks meaningless. But this is needed in order
    # to avoid weak reference
    args, kwargs = yield lambda step_coro: Clock.schedule_once(
        partial(step_coro), duration)
    return args[0]


@types.coroutine
def event(ed, name, *, filter=None, return_value=None):
    bind_id = None
    step_coro = None

    def bind(step_coro_):
        nonlocal bind_id, step_coro
        bind_id = ed.fbind(name, callback)
        assert bind_id > 0  # check if binding succeeded
        step_coro = step_coro_

    def callback(*args, **kwargs):
        if (filter is not None) and (not filter(*args, **kwargs)):
            return
        ed.unbind_uid(name, bind_id)
        step_coro(*args, **kwargs)
        return return_value

    return (yield bind)
