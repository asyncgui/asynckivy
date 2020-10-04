'''The entire module is experimental'''

__all__ = ('run_awaitable', )
import warnings
from inspect import iscoroutinefunction, isawaitable
from functools import wraps
import trio
import asynckivy


async def _ak_awaitable_wrapper(
        outcome:dict, end_signal:asynckivy.Event, ak_awaitable):
    try:
        outcome['return_value'] = await ak_awaitable
    except Exception as e:
        outcome['exception'] = e
    finally:
        end_signal.set()


async def run_awaitable(
        ak_awaitable, *, task_status=trio.TASK_STATUS_IGNORED):
    '''(experimental)
    Run an asynckivy-flavored awaitable under Trio.
    
    Usage:
        nursery.start_soon(run_awaitable, asynckivy_flavored_awaitable)
    '''
    end_signal = trio.Event()
    try:
        outcome = {}
        wrapper_coro = _ak_awaitable_wrapper(
            outcome, end_signal, ak_awaitable, )
        asynckivy.start(wrapper_coro)
        task_status.started(wrapper_coro)
        await end_signal.wait()
        exception = outcome.get('exception', None)
        if exception is not None:
            raise exception
    finally:
        wrapper_coro.close()
