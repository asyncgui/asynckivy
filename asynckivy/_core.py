'''Everything in this module doesn't depend on Kivy.'''

__all__ = ('start', 'or_', 'and_', 'Event', )

import types
import typing
from inspect import getcoroutinestate, CORO_CLOSED


def start(coro):
    '''Starts a asynckivy-flavored coroutine.
    Returns the argument itself.
    '''
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

    return coro


class Task:
    '''(internal)'''
    __slots__ = ('coro', 'done', 'result', 'done_callback')
    def __init__(self):
        self.coro = None
        self.done = False
        self.result = None
        self.done_callback = None
    def run(self, coro, *, done_callback=None):
        if self.coro is not None:
            raise Exception("'run()' can be called only once.")
        self.done_callback = done_callback
        self.coro = start(self._wrapper(coro))
    async def _wrapper(self, inner_coro):
        self.result = await inner_coro
        self.done = True
        if self.done_callback is not None:
            self.done_callback()
    def cancel(self):
        self.coro.close()


@types.coroutine
def gather(coros:typing.Iterable[typing.Coroutine], *, n:int=None) -> typing.Sequence[Task]:
    '''(internal)'''
    coros = tuple(coros)
    n_coros_left = n if n is not None else len(coros)

    def step_coro(*args, **kwargs):
        nonlocal n_coros_left; n_coros_left -= 1
    def done_callback():
        nonlocal n_coros_left
        n_coros_left -= 1
        if n_coros_left == 0:
            step_coro()
    tasks = tuple(Task() for coro in coros)
    for task, coro in zip(tasks, coros):
        task.run(coro, done_callback=done_callback)

    if n_coros_left <= 0:
        return tasks

    def callback(step_coro_):
        nonlocal step_coro
        step_coro = step_coro_
    yield callback

    return tasks


async def or_(*coros):
    return await gather(coros, n=1)


async def and_(*coros):
    return await gather(coros)


class Event:
    '''Similar to 'trio.Event'. The difference is this one allows the user to
    pass data:

        import asynckivy as ak

        e = ak.Event()
        async def task(e):
            assert await e.wait() == 'A'
        ak.start(task(e))
        e.set('A')
    '''
    __slots__ = ('_value', '_flag', '_step_coro_list', )

    def __init__(self):
        self._value = None
        self._flag = False
        self._step_coro_list = []

    def is_set(self):
        return self._flag

    def set(self, value=None):
        if self._flag:
            return
        self._flag = True
        self._value = value
        step_coro_list = self._step_coro_list
        self._step_coro_list = []
        for step_coro in step_coro_list:
            step_coro(value)

    def clear(self):
        self._flag = False

    @types.coroutine
    def wait(self):
        if self._flag:
            yield lambda step_coro: step_coro()
            return self._value
        else:
            return (yield self._step_coro_list.append)[0][0]


@types.coroutine
def _get_step_coro():
    '''(internal)'''
    return (yield lambda step_coro: step_coro(step_coro))[0][0]
