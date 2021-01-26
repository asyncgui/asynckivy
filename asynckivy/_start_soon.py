__all__ = ('start_soon', )

from kivy.clock import Clock
from asynckivy import Awaitable_or_Task, Task

_waiting = []


def _start(dt):
    from asynckivy import start
    global _waiting
    waiting = _waiting
    _waiting = []
    for task in waiting:
        start(task)


_trigger_start = Clock.create_trigger(_start, 0)


def start_soon(awaitable_or_task: Awaitable_or_Task) -> Task:
    '''
    Schedules a awaitable/Task to start after the next frame.

    If the argument is a Task, itself will be returned. If it's an awaitable,
    it will be wrapped in a Task, and the Task will be returned.
    '''
    if isinstance(awaitable_or_task, Task):
        task = awaitable_or_task
    else:
        task = Task(awaitable_or_task)
    _waiting.append(task)
    _trigger_start()
    return task
