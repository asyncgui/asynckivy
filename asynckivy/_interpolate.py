__all__ = ('interpolate', 'fade_transition', )
from contextlib import asynccontextmanager
import types
from functools import partial
from kivy.clock import Clock
from kivy.animation import AnimationTransition


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

    =========== =====
    progress    print
    =========== =====
    0 sec       0
    0.3 sec     30
    0.6 sec     60
    0.9 sec     90
    **1.2 sec** 100
    =========== =====

    Keyword-arguments are the same as ``kivy.animation.Animation``'s.

    .. _interpolate: https://wasabi2d.readthedocs.io/en/stable/coros.html#clock.coro.interpolate  # noqa: E501
    '''
    from asyncgui import get_step_coro
    duration = kwargs.pop('d', kwargs.pop('duration', 1.))
    transition = kwargs.pop('t', kwargs.pop('transition', 'linear'))
    step = kwargs.pop('s', kwargs.pop('step', 0))
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)
    if kwargs:
        raise ValueError(f"unrecognizable keyword-arguments: {kwargs}")

    yield start
    if not duration:
        yield end
        return
    try:
        clock_event = Clock.schedule_interval(
            partial(_update, start, end, duration, transition, await get_step_coro(), [0., ],),
            step,
        )

        get_current_value = _get_current_value
        while True:
            # TODO: refactor when drop python 3.7
            value = await get_current_value()
            if value is None:
                break
            else:
                yield value
    finally:
        clock_event.cancel()


def _update(start, end, duration, transition, step_coro, p_time, dt):
    time = p_time[0] + dt
    p_time[0] = time

    # calculate progression
    progress = min(1., time / duration)
    t = transition(progress)

    value = (start * (1. - t)) + (end * t)
    step_coro(value)

    # time to stop ?
    if progress >= 1.:
        step_coro(None)
        return False


@types.coroutine
def _get_current_value():
    return (yield lambda step_coro: None)[0][0]


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
