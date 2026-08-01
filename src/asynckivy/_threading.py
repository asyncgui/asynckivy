from threading import Thread
from concurrent.futures import Executor
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


async def run_in_thread(func, *, daemon=None):
    '''
    Creates a new thread, runs a function within it, then waits for the completion of that function.

    .. code-block::

        return_value = await run_in_thread(func)

    See :ref:`io-in-asynckivy` for details.

    .. warning::
        When the caller Task is cancelled, the ``func`` will be left running, which violates structured concurrency.
        Also, do not call this function from outside the main thread unless you know what you're doing.
    '''
    ev = asyncgui.ExclusiveEvent()
    Thread(
        name='asynckivy.run_in_thread',
        target=_wrapper, daemon=daemon, args=(func, ev, ),
    ).start()
    ret, exc = (await ev.wait())[0]
    if exc is not None:
        raise exc
    return ret


async def run_in_executor(executor: Executor, func, *args):
    '''
    Runs a function within a :class:`concurrent.futures.Executor`, and waits for the completion of the
    function.

    .. code-block::

        executor = ThreadPoolExecutor()
        ...
        return_value = await run_in_executor(executor, func)

    :param args: Arguments to pass to the ``executor.submit`` method.

    .. warning::
        When the caller Task is cancelled, the ``func`` will be left running if it has already started,
        which violates structured concurrency.
        Also, do not call this function from outside the main thread unless you know what you're doing.

    .. versionchanged:: 0.11.1
        Added support for passing arguments to the ``executor.submit`` method.
        Added support for :class:`~concurrent.futures.ProcessPoolExecutor` and
        :class:`~concurrent.futures.InterpreterPoolExecutor`.
    '''
    ev = asyncgui.ExclusiveEvent()
    fut = executor.submit(func, *args)
    fut.add_done_callback(lambda __: Clock.schedule_once(ev.fire))
    try:
        await ev.wait()
    except asyncgui.Cancelled:
        fut.cancel()
        raise
    return fut.result()
