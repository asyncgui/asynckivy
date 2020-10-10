__all__ = ('animate', 'animation', )
import types
from functools import partial
from kivy.clock import Clock
from kivy.animation import AnimationTransition
from asynckivy import sleep, sleep_forever


async def animate(target, **kwargs):
    '''An asynchronous version of `kivy.animation.Animation`.

    Usage:
        await animate(widget, x=100, d=2, s=.2, t='in_cubic')

    A notable difference is `force_final_value`, which ensures the final-value
    of an animation to be applied even when it is cancelled.

        import asynckivy as ak
        widget.x = 0
        coro = ak.start(ak.animate(widget, x=100, force_final_value=True))
        coro.close()
        assert widget.x == 100
    '''
    from asynckivy._core import _get_step_coro
    duration = kwargs.pop('d', kwargs.pop('duration', 1.))
    transition = kwargs.pop('t', kwargs.pop('transition', 'linear'))
    step = kwargs.pop('s', kwargs.pop('step', 0))
    force_final_value = kwargs.pop('force_final_value', False)
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)
    animated_properties = kwargs

    # get current values
    properties = {}
    for key, value in animated_properties.items():
        original_value = getattr(target, key)
        if isinstance(original_value, (tuple, list)):
            original_value = original_value[:]
        elif isinstance(original_value, dict):
            original_value = original_value.copy()
        properties[key] = (original_value, value)

    if not duration:
        await sleep(0)
        _set_final_value(target, properties)
        return

    try:
        ctx = {
            'target': target,
            'time': 0.,
            'duration': duration,
            'transition': transition,
            'properties': properties,
            'step_coro': await _get_step_coro(),
        }
        clock_event = Clock.schedule_interval(partial(_update, ctx), step)
        await sleep_forever()
    except GeneratorExit:
        if force_final_value:
            _set_final_value(target, properties)
        raise
    finally:
        clock_event.cancel()


def _update(ctx, dt):
    time = ctx['time'] + dt
    ctx['time'] = time

    # calculate progression
    progress = min(1., time / ctx['duration'])
    t = ctx['transition'](progress)

    # apply progression on target
    target = ctx['target']
    for key, values in ctx['properties'].items():
        a, b = values
        value = _calculate(a, b, t)
        setattr(target, key, value)

    # time to stop ?
    if progress >= 1.:
        ctx['step_coro']()
        return False


def _set_final_value(target, properties):
    for key, values in properties.items():
        setattr(target, key, values[1])


def _calculate(a, b, t):
    if isinstance(a, list) or isinstance(a, tuple):
        if isinstance(a, list):
            tp = list
        else:
            tp = tuple
        return tp([_calculate(a[x], b[x], t) for x in range(len(a))])
    elif isinstance(a, dict):
        d = {}
        for x in a:
            if x not in b:
                # User requested to animate only part of the dict.
                # Copy the rest
                d[x] = a[x]
            else:
                d[x] = _calculate(a[x], b[x], t)
        return d
    else:
        return (a * (1. - t)) + (b * t)


animation = animate
