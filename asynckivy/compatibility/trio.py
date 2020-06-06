__all__ = ('run_coro_under_trio', )
from functools import wraps
import trio
import asynckivy


async def run_coro_under_trio(coro, *, task_status=trio.TASK_STATUS_IGNORED):
    '''(experimental) Run an asynckivy-flavored coroutine under Trio
    
    Usage:
        nursery.start_soon(run_coro_under_trio, asynckivy_flavored_coro)
    '''
    event = trio.Event()
    async def wrapper():
        await coro
        event.set()
    try:
        wrapper_coro = wrapper()
        asynckivy.start(wrapper_coro)
        task_status.started(wrapper_coro)
        await event.wait()
    finally:
        wrapper_coro.close()
