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

    return partial(_update, target, duration, transition, properties, lambda: None, [0., ])


def _calculate(a, b, t, isinstance=isinstance, list=list, tuple=tuple, dict=dict):
    '''The logic of this function is identical to 'kivy.animation.Animation._calculate()'
    '''
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


def _update(target, duration, transition, properties, step_coro, p_time, dt, _calculate=_calculate, setattr=setattr):
    time = p_time[0] + dt
    p_time[0] = time

    # calculate progression
    progress = min(1., time / duration)
    t = transition(progress)

    # apply progression on target
    target = target
    for key, values in properties.items():
        a, b = values
        value = _calculate(a, b, t)
        setattr(target, key, value)

    # time to stop ?
    if progress >= 1.:
        step_coro()
        return False
