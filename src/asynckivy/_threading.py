__all__ = ('run_in_thread', 'run_in_executor', )
import typing as T
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from kivy.clock import Clock
import asyncgui


def _wrapper(func, ev):
    ret = None
    exc = None
    try:
        ret = func()
    except Exception as e:
        exc = e
    finally:
        Clock.schedule_once(lambda __: ev.fire(ret, exc))


async def run_in_thread(func, *, daemon=None) -> T.Awaitable:
    '''
    Creates a new thread, runs a function within it, then waits for the completion of that function.

    .. code-block::

        return_value = await run_in_thread(func)

    See :ref:`io-in-asynckivy` for details.
    '''
    ev = asyncgui.AsyncEvent()
    Thread(
        name='asynckivy.run_in_thread',
        target=_wrapper, daemon=daemon, args=(func, ev, ),
    ).start()
    ret, exc = (await ev.wait())[0]
    if exc is not None:
        raise exc
    return ret


async def run_in_executor(executor: ThreadPoolExecutor, func) -> T.Awaitable:
    '''
    Runs a function within a :class:`concurrent.futures.ThreadPoolExecutor`, and waits for the completion of the
    function.

    .. code-block::

        executor = ThreadPoolExecutor()
        ...
        return_value = await run_in_executor(executor, func)

    See :ref:`io-in-asynckivy` for details.
    '''
    ev = asyncgui.AsyncEvent()
    future = executor.submit(_wrapper, func, ev)
    try:
        ret, exc = (await ev.wait())[0]
    except asyncgui.Cancelled:
        future.cancel()
        raise
    assert future.done()
    if exc is not None:
        raise exc
    return ret
