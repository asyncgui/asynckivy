__all__ = ('run_in_thread', )
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
