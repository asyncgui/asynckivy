'''Everything in this module doesn't depend on Kivy.'''

__all__ = (
    'start', 'sleep_forever', 'or_', 'and_', 'Event', 'Task', 'TaskState',
    'get_current_task',
)

import itertools
import types
import typing
from inspect import (
    getcoroutinestate, CORO_CLOSED, CORO_CREATED,
    isawaitable,
)
import enum

from asynckivy import exceptions


class TaskState(enum.Flag):
    CREATED = enum.auto()  # CORO_CREATED
    STARTED = enum.auto()  # CORO_RUNNING or CORO_SUSPENDED
    CANCELLED = enum.auto()  # CORO_CLOSED by coro.close() or some exception
    DONE = enum.auto()  # CORO_CLOSED
    ENDED = CANCELLED | DONE


class Task:
    '''(experimental)
    Similar to `asyncio.Task`. The main difference is that this one is not
    awaitable.

    Usage:

        import asynckivy as ak

        async def async_fn():
            task = ak.Task(some_awaitable, name='my_sub_task')
            ak.start(task)
            ...
            ...
            ...

            # case #1 wait for the completion of the task.
            await task.wait()
            print(task.result)

            # case #2 wait for the cancellation of the task.
            await task.wait(ak.TaskState.CANCELLED)

            # case #3 wait for both completion and cancellation of the task.
            await task.wait(ak.TaskState.ENDED)
            if task.done:
                print(task.result)
    '''

    __slots__ = (
        'name', '_uid', '_root_coro', '_state', '_result', '_event',
    )

    _uid_iter = itertools.count()

    def __init__(self, awaitable, *, name=''):
        if not isawaitable(awaitable):
            raise ValueError(str(awaitable) + " is not awaitable.")
        self._uid = next(self._uid_iter)
        self.name:str = name
        self._root_coro = self._wrapper(awaitable)
        self._state = TaskState.CREATED
        self._event = Event()

    def __str__(self):
        return f'Task(uid={self._uid}, name={self.name!r})'

    @property
    def uid(self) -> int:
        return self._uid

    @property
    def root_coro(self) -> typing.Coroutine:
        return self._root_coro

    @property
    def state(self) -> TaskState:
        return self._state

    @property
    def done(self) -> bool:
        return self._state is TaskState.DONE

    @property
    def cancelled(self) -> bool:
        return self._state is TaskState.CANCELLED

    @property
    def result(self):
        '''Equivalent of asyncio.Future.result()'''
        state = self._state
        if state is TaskState.DONE:
            return self._result
        elif state is TaskState.CANCELLED:
            raise exceptions.CancelledError(f"{self} was cancelled")
        else:
            raise exceptions.InvalidStateError(f"Result of {self} is not ready")

    async def _wrapper(self, awaitable):
        try:
            self._state = TaskState.STARTED
            self._result = await awaitable
        except GeneratorExit:
            self._state = TaskState.CANCELLED
            raise
        except:
            from asynckivy.utils import get_logger
            logger = get_logger(__name__)
            logger.critical('Uncaught exception on ' + str(self))
            self._state = TaskState.CANCELLED
            raise
        else:
            self._state = TaskState.DONE
        finally:
            self._event.set(self)

    def cancel(self):
        self._root_coro.close()

    async def wait(self, wait_for:TaskState=TaskState.DONE):
        '''Wait for the Task to be cancelled or done.

        'wait_for' must be one of the following:

            TaskState.DONE (default)
            TaskState.CANCELLED
            TaskState.ENDED
        '''
        if wait_for & (~TaskState.ENDED):
            raise ValueError("'wait_for' is incorrect:", wait_for)
        await self._event.wait()
        if self.state & wait_for:
            return
        await sleep_forever()


Coro_or_Task = typing.Union[typing.Coroutine, Task]


def start(coro_or_task:Coro_or_Task) -> Coro_or_Task:
    '''Starts a asynckivy-flavored coroutine or a Task. It is recommended to
    pass a Task instead of a coroutine if a coroutine is going to live long
    time, as Task is flexibler and has information that may be useful for
    debugging.

    Returns the argument itself.
    '''
    def step_coro(*args, **kwargs):
        try:
            if getcoroutinestate(coro) != CORO_CLOSED:
                coro.send((args, kwargs, ))(step_coro)
        except StopIteration:
            pass

    if isinstance(coro_or_task, Task):
        task = coro_or_task
        if task._state is not TaskState.CREATED:
            raise ValueError(f"{task} was already started")
        step_coro._task = task
        coro = task.root_coro
    else:
        coro = coro_or_task
        if getcoroutinestate(coro) != CORO_CREATED:
            raise ValueError("Coroutine was already started")
        step_coro._task = None

    try:
        coro.send(None)(step_coro)
    except StopIteration:
        pass

    return coro_or_task


@types.coroutine
def sleep_forever():
    yield lambda step_coro: None


Awaitable_or_Task = typing.Union[typing.Awaitable, Task]


@types.coroutine
def gather(aws_and_tasks:typing.Iterable[Awaitable_or_Task], *, n:int=None) \
        -> typing.Sequence[Task]:
    '''(internal)'''
    tasks = tuple(
        v if isinstance(v, Task) else Task(v) for v in aws_and_tasks)
    n_left = n if n is not None else len(tasks)

    def step_coro():
        pass
    def done_callback(__):
        nonlocal n_left
        n_left -= 1
        if n_left == 0:
            step_coro()
    for task in tasks:
        task._event.add_callback(done_callback)
        start(task)

    if n_left <= 0:
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
    pass value:

        import asynckivy as ak

        e = ak.Event()
        async def task():
            assert await e.wait() == 'A'
        ak.start(task())
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

    def add_callback(self, callback):
        '''(internal)'''
        if self._flag:
            callback(self._value)
        else:
            self._step_coro_list.append(callback)


@types.coroutine
def _get_step_coro():
    '''(internal)'''
    return (yield lambda step_coro: step_coro(step_coro))[0][0]


@types.coroutine
def get_current_task() -> typing.Optional[Task]:
    '''Returns the task currently running. None if no Task is associated.'''
    return (yield lambda step_coro: step_coro(step_coro._task))[0][0]
