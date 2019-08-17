__version__ = '0.0.1'
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


class event:
    def __init__(self, ed, name, *, filter=None):
        self.bind_id = None
        self.ed = ed
        self.name = name
        self.filter = filter

    def bind(self, step_coro):
        self.bind_id = bind_id = self.ed.fbind(self.name, self.callback)
        assert bind_id > 0  # check if binding succeeded
        self.step_coro = step_coro

    def callback(self, *args, **kwargs):
        if (self.filter is not None) and (not self.filter(*args, **kwargs)):
            return
        self.parameter = (args, kwargs, )
        ed = self.ed
        ed.unbind_uid(self.name, self.bind_id)
        self.step_coro()

    def __await__(self):
        yield self.bind
        return self.parameter
