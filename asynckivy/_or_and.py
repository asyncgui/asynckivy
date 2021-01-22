__all__ = ('and_', 'or_', 'and_from_iterable', 'or_from_iterable', )

import types
from typing import Iterable, List
from asyncgui import Task, Awaitable_or_Task


@types.coroutine
def _gather(aws_and_tasks: Iterable[Awaitable_or_Task], *, n: int = None) \
        -> List[Task]:
    '''(internal)'''
    from asynckivy import start, close_soon

    def do_nothing():
        pass

    tasks = [v if isinstance(v, Task) else Task(v) for v in aws_and_tasks]
    n_tasks = len(tasks)
    n_left = n_tasks if n is None else min(n, n_tasks)
    step_coro = do_nothing

    def done_callback(*args, **kwargs):
        nonlocal n_left
        n_left -= 1
        if n_left == 0:
            step_coro()

    try:
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
    finally:
        step_coro = do_nothing
        for task in tasks:
            if task.is_cancellable:
                task.cancel()
            else:
                close_soon(task)


async def or_(*aws_and_tasks: Iterable[Awaitable_or_Task]):
    return await _gather(aws_and_tasks, n=1)


async def or_from_iterable(aws_and_tasks: Iterable[Awaitable_or_Task]):
    return await _gather(aws_and_tasks, n=1)


async def and_(*aws_and_tasks: Iterable[Awaitable_or_Task]):
    return await _gather(aws_and_tasks)


async def and_from_iterable(aws_and_tasks: Iterable[Awaitable_or_Task]):
    return await _gather(aws_and_tasks)
