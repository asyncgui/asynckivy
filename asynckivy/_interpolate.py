__all__ = ('interpolate', )
import types
from functools import partial
from kivy.clock import Clock
from kivy.animation import AnimationTransition


async def interpolate(start, end, **kwargs):
    '''Interpolate between the values start and end.

    Usage:

        async for v in asynckivy.interpolate(0, 100, d=1., s=.3, t='linear'):
            print(v)  # prints 0 immediately
                      # prints 30 after 0.3 seconds
                      # prints 60 after 0.6 seconds
                      # prints 90 after 0.9 seconds
                      # prints 100 after 1.2 seconds
    
    Available keyword arguments are the same as `animate()`.

    Inspired by wasabi2d.
    '''
    from asynckivy._core import _get_step_coro
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
        ctx = {
            'start': start,
            'end': end,
            'time': 0.,
            'duration': duration,
            'transition': transition,
            'step_coro': await _get_step_coro(),
        }
        clock_event = Clock.schedule_interval(partial(_update, ctx), step)

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


def _update(ctx, dt):
    time = ctx['time'] + dt
    ctx['time'] = time

    # calculate progression
    progress = min(1., time / ctx['duration'])
    t = ctx['transition'](progress)

    value = (ctx['start'] * (1. - t)) + (ctx['end'] * t)
    ctx['step_coro'](value)

    # time to stop ?
    if progress >= 1.:
        ctx['step_coro'](None)
        return False


@types.coroutine
def _get_current_value() -> int:
    return (yield lambda step_coro: None)[0][0]
