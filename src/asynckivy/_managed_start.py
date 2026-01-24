import asyncgui as ag
from asyncgui import Task, start
from kivy.base import EventLoop


_managed_tasks = []
_n_until_gc = _GC_IN_EVERY = 1000


def _collect_garbage(STARTED=ag.TaskState.STARTED):
    global _managed_tasks
    _managed_tasks = [task for task in _managed_tasks if task.state is STARTED]


def managed_start(aw: ag.Aw_or_Task, /) -> Task:
    '''
    A task started with this function will be automatically cancelled when an ``EventLoop.on_stop``
    event fires, if it is still running. This prevents the task from being cancelled by the garbage
    collector, ensuring more reliable cleanup. You should always use this function instead of calling
    ``asynckivy.start`` directly, except when writing unit tests.

    .. code-block::

        task = managed_start(async_func(...))

    .. versionadded:: 0.7.1
    .. versionchanged:: 0.10.0
        Uses ``EventLoop.on_stop`` instead of ``App.on_stop``.
    '''
    global _n_until_gc
    task = start(aw)
    _managed_tasks.append(task)
    _n_until_gc -= 1
    if _n_until_gc <= 0:
        _n_until_gc = _GC_IN_EVERY
        _collect_garbage()
    return task


def cancel_managed_tasks(*__):
    '''
    Cancels all tasks started with :func:`managed_start`.

    Usually, you do not need to call this function directly, as it is automatically called when an
    ``EventLoop.on_stop`` event fires. However, you might need to call it manually in unit tests because
    the ``EventLoop.on_stop`` event wouldn't be triggered in each test case.

    .. versionadded:: 0.10.0
    '''
    global _managed_tasks
    tasks = _managed_tasks
    _managed_tasks = []
    for t in tasks:
        t.cancel()


EventLoop.fbind("on_stop", cancel_managed_tasks)
