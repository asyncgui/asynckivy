__all__ = ('start_soon', )

from kivy.clock import Clock


_waiting = []


def _start(dt):
    from asynckivy import start
    global _waiting
    waiting = _waiting
    _waiting = []
    for coro_or_task in waiting:
        start(coro_or_task)


_trigger_start = Clock.create_trigger(_start, 0)


def start_soon(coro_or_task):
    '''
    Schedules a coroutine/Task to start after the next frame.
    Returns the argument itself.
    '''
    _waiting.append(coro_or_task)
    _trigger_start()
    return coro_or_task
