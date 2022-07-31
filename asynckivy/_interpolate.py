__all__ = ('interpolate', 'fade_transition', )
from contextlib import asynccontextmanager
from kivy.animation import AnimationTransition

from ._sleep import repeat_sleeping


linear_transition = AnimationTransition.linear


async def interpolate(start, end, **kwargs):
    '''
    interpolate
    ===========

    Interpolates between the values ``start`` and ``end`` in an async-manner.
    Inspired by wasabi2d's interpolate_.

    Usage
    -----

    .. code-block:: python

       async for v in asynckivy.interpolate(0, 100, d=1., s=.3, t='linear'):
           print(int(v))

    The code above prints as follows:

    ============ =====
    elapsed time print
    ============ =====
    0 sec        0
    0.3 sec      30
    0.6 sec      60
    0.9 sec      90
    **1.2 sec**  100
    ============ =====

    Keyword-arguments are the same as ``kivy.animation.Animation``'s.

    .. _interpolate: https://wasabi2d.readthedocs.io/en/stable/coros.html#clock.coro.interpolate  # noqa: E501
    '''
    duration = kwargs.pop('d', kwargs.pop('duration', 1.))
    transition = kwargs.pop('t', kwargs.pop('transition', linear_transition))
    step = kwargs.pop('s', kwargs.pop('step', 0))
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)
    if kwargs:
        raise ValueError(f"unrecognizable keyword-arguments: {kwargs}")

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
async def fade_transition(*widgets, **kwargs):
    '''Fade-out/in the given widgets.

    Available keyword-arguments are 'd', 'duration', 's' and 'step'.
    '''
    half_d = kwargs.pop('d', kwargs.pop('duration', 1.)) / 2.
    s = kwargs.pop('s', kwargs.pop('step', 0))
    if kwargs:
        raise ValueError("surplus keyword-arguments were given:", kwargs)
    original_opacities = tuple(w.opacity for w in widgets)
    try:
        async for v in interpolate(1.0, 0.0, d=half_d, s=s):
            for w, o in zip(widgets, original_opacities):
                w.opacity = v * o
        yield
        async for v in interpolate(0.0, 1.0, d=half_d, s=s):
            for w, o in zip(widgets, original_opacities):
                w.opacity = v * o
    except GeneratorExit:
        for w, o in zip(widgets, original_opacities):
            w.opacity = o
        raise
