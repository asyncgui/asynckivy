__all__ = ('create_update', )
from functools import partial
from kivy.animation import AnimationTransition


def create_update(target, **kwargs):
    duration = kwargs.pop('d', kwargs.pop('duration', 1.))
    transition = kwargs.pop('t', kwargs.pop('transition', 'linear'))
    animated_properties = kwargs
    if not duration:
        for key, value in animated_properties.items():
            setattr(target, key, value)
        return
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)

    # get current values
    properties = {}
    for key, value in animated_properties.items():
        original_value = getattr(target, key)
        if isinstance(original_value, (tuple, list)):
            original_value = original_value[:]
        elif isinstance(original_value, dict):
            original_value = original_value.copy()
        properties[key] = (original_value, value)

    ctx = {
        'target': target,
        'time': 0.,
        'duration': duration,
        'transition': transition,
        'properties': properties,
        'step_coro': lambda: None,
    }
    return partial(_update, ctx)


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
