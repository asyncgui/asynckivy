from collections.abc import AsyncIterator
from kivy.animation import AnimationTransition

from ._sleep import sleep, sleep_freq


linear = AnimationTransition.linear


async def interpolate(start, end, *, duration=1.0, step=0, transition=linear) -> AsyncIterator:
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
        with sleep_freq(step) as slp:
            et = 0.  # elapsed time
            while True:
                et += await slp()
                if et >= duration:
                    break
                yield transition(et / duration) * slope + start
    else:
        await sleep(0)
    yield transition(1.) * slope + start


async def interpolate_seq(start, end, *, duration, step=0, transition=linear) -> AsyncIterator:
    '''
    Same as :func:`interpolate` except this one is for sequence types.

    .. code-block::

        async for v in interpolate_seq([0, 50], [100, 100], duration=1, step=0.3):
            print(v)

    ============ ==========
    elapsed time output
    ============ ==========
    0            [0, 50]
    0.3          [30, 65]
    0.6          [60, 80]
    0.9          [90, 95]
    **1.2 sec**  [100, 100]
    ============ ==========

    .. versionadded:: 0.7.0
    .. versionchanged:: 0.9.0
        The ``output_type`` parameter was removed. The iterator now always yields a list.
    '''
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)
    zip_ = zip
    slope = tuple(end_elem - start_elem for end_elem, start_elem in zip_(end, start))

    yield [transition(0.) * slope_elem + start_elem for slope_elem, start_elem in zip_(slope, start)]

    if duration:
        with sleep_freq(step) as slp:
            et = 0.  # elapsed time
            while True:
                et += await slp()
                if et >= duration:
                    break
                yield [transition(et / duration) * slope_elem + start_elem
                       for slope_elem, start_elem in zip_(slope, start)]
    else:
        await sleep(0)

    yield [transition(1.) * slope_elem + start_elem for slope_elem, start_elem in zip_(slope, start)]
