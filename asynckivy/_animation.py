__all__ = ('animation', )


async def animation(target, **kwargs):
    from time import perf_counter as get_current_time
    from kivy.animation import AnimationTransition
    from ._sleep import sleep

    duration = kwargs.pop('d', kwargs.pop('duration', 1.))
    transition = kwargs.pop('t', kwargs.pop('transition', 'linear'))
    step = kwargs.pop('s', kwargs.pop('step', 0))
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

    # assigning to a local variable might improve the performance
    calculate = _calculate

    if not duration:
        await sleep(0)
        for key, values in properties.items():
            a, b = values
            setattr(target, key, b)
        return

    start_time = get_current_time()
    while True:
        await sleep(step)

        # calculate progression
        progress = min(1., (get_current_time() - start_time) / duration)
        t = transition(progress)

        # apply progression on target
        for key, values in properties.items():
            a, b = values
            value = calculate(a, b, t)
            setattr(target, key, value)

        # time to stop ?
        if progress >= 1.:
            return


def _calculate(a, b, t):
    if isinstance(a, list) or isinstance(a, tuple):
        if isinstance(a, list):
            tp = list
        else:
            tp = tuple
        return tp([_calculate(a[x], b[x], t) for x in range(len(a))])
    elif isinstance(a, dict):
        d = {}
        for x in iterkeys(a):
            if x not in b:
                # User requested to animate only part of the dict.
                # Copy the rest
                d[x] = a[x]
            else:
                d[x] = _calculate(a[x], b[x], t)
        return d
    else:
        return (a * (1. - t)) + (b * t)
