__all__ = ('interpolate', 'fade_transition', )
import typing as T
from contextlib import asynccontextmanager
from kivy.animation import AnimationTransition

from asyncgui import Cancelled
from ._sleep import repeat_sleeping


linear = AnimationTransition.linear


async def interpolate(start, end, *, duration=1.0, step=0, transition=linear) -> T.AsyncIterator:
    '''
    Interpolate between the values ``start`` and ``end`` in an async-manner.
    Inspired by wasabi2d's interpolate_.

    .. code-block::

        async for v in interpolate(0, 100, duration=1.0, step=.3):
            print(int(v))

    ============ ======
    elapsed time output
    ============ ======
    0 sec        0
    0.3 sec      30
    0.6 sec      60
    0.9 sec      90
    **1.2 sec**  100
    ============ ======

    **Restriction**

    You are not allowed to perform any kind of async operations inside the with-block.

    .. code-block::

        async for v in interpolate(...):
            await awaitable  # NOT ALLOWED
            async with async_context_manager:  # NOT ALLOWED
                ...
            async for __ in async_iterator:  # NOT ALLOWED
                ...

    .. _interpolate: https://wasabi2d.readthedocs.io/en/stable/coros.html#clock.coro.interpolate
    '''
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)

    yield start
    if not duration:
        yield end
        return

    slope = end - start
    elapsed_time = 0.
    async with repeat_sleeping(step=step) as sleep:
        while True:
            elapsed_time += await sleep()
            if elapsed_time >= duration:
                break
            progress = transition(elapsed_time / duration)
            yield progress * slope + start
    yield end


@asynccontextmanager
async def fade_transition(*widgets, duration=1.0, step=0) -> T.AsyncContextManager:
    '''
    Return an async context manager that:

    * fades-out the given widgets on ``__aenter__``.
    * fades-in the given widgets on ``__aexit__``.

    .. code-block::

        async with fade_transition(widget1, widget2):
            ...
    '''
    half_duration = duration / 2.
    org_opacity = tuple(w.opacity for w in widgets)
    try:
        async for v in interpolate(1.0, 0.0, duration=half_duration, step=step):
            for w, o in zip(widgets, org_opacity):
                w.opacity = v * o
        yield
        async for v in interpolate(0.0, 1.0, duration=half_duration, step=step):
            for w, o in zip(widgets, org_opacity):
                w.opacity = v * o
    except Cancelled:
        for w, o in zip(widgets, org_opacity):
            w.opacity = o
        raise
