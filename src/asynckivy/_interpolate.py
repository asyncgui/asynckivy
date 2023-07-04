__all__ = ('interpolate', 'fade_transition', )
from contextlib import asynccontextmanager
from kivy.animation import AnimationTransition

from asyncgui import Cancelled
from ._sleep import repeat_sleeping


linear_transition = AnimationTransition.linear


async def interpolate(start, end, *, duration=1.0, step=0, transition=AnimationTransition.linear):
    '''
    interpolate
    ===========

    Interpolates between the values ``start`` and ``end`` in an async-manner.
    Inspired by wasabi2d's interpolate_.

    Usage
    -----

    .. code-block:: python

        async for v in asynckivy.interpolate(0, 100, duration=1.0, step=.3):
            print(int(v))

    The above code prints as follows:

    ============ =====
    elapsed time print
    ============ =====
    0 sec        0
    0.3 sec      30
    0.6 sec      60
    0.9 sec      90
    **1.2 sec**  100
    ============ =====

    .. _interpolate: https://wasabi2d.readthedocs.io/en/stable/coros.html#clock.coro.interpolate  # noqa: E501
    '''
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)

    yield start
    if not duration:
        yield end
        return

    slope = end - start
    elapsed_time = 0.
    async with repeat_sleeping(step) as sleep:
        while True:
            elapsed_time += await sleep()
            if elapsed_time >= duration:
                break
            progress = transition(elapsed_time / duration)
            yield progress * slope + start
    yield end


@asynccontextmanager
async def fade_transition(*widgets, duration=1.0, step=0):
    '''Return an async context manager that fades-out/in the given widgets.
    '''
    half_duration = duration / 2.
    original_opacities = tuple(w.opacity for w in widgets)
    try:
        async for v in interpolate(1.0, 0.0, duration=half_duration, step=step):
            for w, o in zip(widgets, original_opacities):
                w.opacity = v * o
        yield
        async for v in interpolate(0.0, 1.0, duration=half_duration, step=step):
            for w, o in zip(widgets, original_opacities):
                w.opacity = v * o
    except Cancelled:
        for w, o in zip(widgets, original_opacities):
            w.opacity = o
        raise
