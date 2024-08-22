__all__ = ('interpolate', 'interpolate_seq', 'fade_transition', )
import typing as T
from contextlib import asynccontextmanager
from kivy.animation import AnimationTransition

from ._sleep import sleep
from ._anim_with_xxx import anim_with_ratio


linear = AnimationTransition.linear


async def interpolate(start, end, *, duration=1.0, step=0, transition=linear) -> T.AsyncIterator:
    '''
    Interpolates between the values ``start`` and ``end`` in an async-manner.
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

    .. _interpolate: https://wasabi2d.readthedocs.io/en/stable/coros.html#clock.coro.interpolate
    '''
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)

    slope = end - start
    yield transition(0.) * slope + start
    if duration:
        async for p in anim_with_ratio(step=step, base=duration):
            if p >= 1.0:
                break
            yield transition(p) * slope + start
    else:
        await sleep(0)
    yield transition(1.) * slope + start


async def interpolate_seq(start, end, *, duration, step=0, transition=linear, output_type=tuple) -> T.AsyncIterator:
    '''
    Same as :func:`interpolate` except this one is for sequence types.

    .. code-block::

        async for v in interpolate_seq([0, 50], [100, 100], duration=1, step=0.3):
            print(v)

    ============ ==========
    elapsed time output
    ============ ==========
    0            (0, 50)
    0.3          (30, 65)
    0.6          (60, 80)
    0.9          (90, 95)
    **1.2 sec**  (100, 100)
    ============ ==========

    .. versionadded:: 0.7.0
    '''
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)
    zip_ = zip
    slope = tuple(end_elem - start_elem for end_elem, start_elem in zip_(end, start))

    p = transition(0.)
    yield output_type(p * slope_elem + start_elem for slope_elem, start_elem in zip_(slope, start))

    if duration:
        async for p in anim_with_ratio(step=step, base=duration):
            if p >= 1.0:
                break
            p = transition(p)
            yield output_type(p * slope_elem + start_elem for slope_elem, start_elem in zip_(slope, start))
    else:
        await sleep(0)

    p = transition(1.)
    yield output_type(p * slope_elem + start_elem for slope_elem, start_elem in zip_(slope, start))


@asynccontextmanager
async def fade_transition(*widgets, duration=1.0, step=0) -> T.AsyncContextManager:
    '''
    Returns an async context manager that:

    * fades-out the given widgets on ``__aenter__``.
    * fades-in the given widgets on ``__aexit__``.

    .. code-block::

        async with fade_transition(widget1, widget2):
            ...

    The ``widgets`` don't have to be actual Kivy widgets.
    Anything that has an attribute named ``opacity`` would work.
    '''
    half_duration = duration / 2.
    org_opas = tuple(w.opacity for w in widgets)
    try:
        async for p in anim_with_ratio(base=half_duration, step=step):
            p = 1.0 - p
            for w, o in zip(widgets, org_opas):
                w.opacity = p * o
            if p <= 0.:
                break
        yield
        async for p in anim_with_ratio(base=half_duration, step=step):
            for w, o in zip(widgets, org_opas):
                w.opacity = p * o
            if p >= 1.:
                break
    finally:
        for w, o in zip(widgets, org_opas):
            w.opacity = o
