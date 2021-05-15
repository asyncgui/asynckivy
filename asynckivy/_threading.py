__all__ = ('run_in_thread', 'run_in_executer', )
from threading import Thread
from kivy.clock import Clock
import asynckivy


def _wrapper(func, event):
    ret = None
    exc = None
    try:
        ret = func()
    except Exception as e:
        exc = e
    finally:
        Clock.schedule_once(lambda __: event.set((ret, exc, )))


async def run_in_thread(func, *, daemon=False):
    event = asynckivy.Event()
    Thread(
        name='asynckivy.run_in_thread',
        target=_wrapper, daemon=daemon, args=(func, event, ),
    ).start()
    ret, exc = await event.wait()
    if exc is not None:
        raise exc
    return ret


async def run_in_executer(func, executer):
    event = asynckivy.Event()
    future = executer.submit(_wrapper, func, event)
    try:
        ret, exc = await event.wait()
    except GeneratorExit:
        future.cancel()
        raise
    assert future.done()
    if exc is not None:
        raise exc
    return ret
