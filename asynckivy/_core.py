'''Everything in this module doesn't depend on Kivy.'''

__all__ = ('start', 'or_', 'and_', 'Event', 'AutoCloseProperty', )

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
    def __init__(self, coro, *, done_callback=None):
        self.coro = coro
        self.done = False
        self.result = None
        self.done_callback = done_callback
    async def _run(self):
        self.result = await self.coro
        self.done = True
        if self.done_callback is not None:
            self.done_callback()


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
    tasks = tuple(Task(coro, done_callback=done_callback) for coro in coros)
    for task in tasks:
        start(task._run())

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
    '''Equivalent of 'trio.Event'
    '''
    __slots__ = ('_flag', '_step_coro_list')

    def __init__(self):
        self._flag = False
        self._step_coro_list = []

    def is_set(self):
        return self._flag

    def set(self):
        if self._flag:
            return
        self._flag = True
        step_coro_list = self._step_coro_list
        self._step_coro_list = []
        for step_coro in step_coro_list:
            step_coro()

    def clear(self):
        self._flag = False

    @types.coroutine
    def wait(self):
        yield (lambda step_coro: step_coro()) if self._flag \
            else self._step_coro_list.append


@types.coroutine
def _get_step_coro():
    '''(internal)'''
    return (yield lambda step_coro: step_coro(step_coro))[0][0]


class AutoCloseProperty:
    '''A data descriptor, that automatically calls `.close()` when a new value
    is set.

    How it works:

        class Owner:
            coro = AutoCloseProperty()

        owner = Owner()
        owner.coro = coro1 = async_fn()
        owner.coro = coro2 = async_fn()  # 'coro1.close()' will be called.
        owner.coro = None                # 'coro2.close()' will be called.
        owner.coro = coro3 = async_fn()
        del owner.coro                   # 'coro3.close()' will be called.

    Setting the same value won't trigger '.close()':

        owner = Owner()
        owner.coro = coro1 = async_fn()
        owner.coro = coro1               # 'coro1.close()' won't be called.
    '''

    def __set_name__(self, klass, name):
        self.name = name

    def __get__(self, obj, klass=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, new_value):
        old_value = obj.__dict__.get(self.name)
        if old_value is new_value:
            return
        if old_value is not None:
            old_value.close()
        obj.__dict__[self.name] = new_value

    def __delete__(self, obj):
        value = obj.__dict__.get(self.name)
        if value is not None:
            value.close()
        del obj.__dict__[self.name]
