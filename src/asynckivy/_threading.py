__all__ = ('run_in_thread', 'run_in_executor', )
from threading import Thread
from kivy.clock import Clock
import asyncgui


def _wrapper(func, box):
    ret = None
    exc = None
    try:
        ret = func()
    except Exception as e:
        exc = e
    finally:
        Clock.schedule_once(lambda __: box.put(ret, exc))


async def run_in_thread(func, *, daemon=False):
    box = asyncgui.IBox()
    Thread(
        name='asynckivy.run_in_thread',
        target=_wrapper, daemon=daemon, args=(func, box, ),
    ).start()
    ret, exc = (await box.get())[0]
    if exc is not None:
        raise exc
    return ret


async def run_in_executor(executor, func):
    box = asyncgui.IBox()
    future = executor.submit(_wrapper, func, box)
    try:
        ret, exc = (await box.get())[0]
    except asyncgui.Cancelled:
        future.cancel()
        raise
    assert future.done()
    if exc is not None:
        raise exc
    return ret
