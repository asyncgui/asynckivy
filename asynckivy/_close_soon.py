__all__ = ('close_soon', )

from kivy.clock import Clock


_waiting = []


def _close(dt):
    global _waiting
    waiting = _waiting
    _waiting = []
    for coro_or_task in waiting:
        coro_or_task.close()


_trigger_close = Clock.create_trigger(_close, -1)


def close_soon(coro_or_task):
    '''
    Schedules a coroutine/Task to close before the next frame.
    '''
    _waiting.append(coro_or_task)
    _trigger_close()
    return coro_or_task
