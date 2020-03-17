__all__ = ('animation', 'animate', )


async def animation(target, **kwargs):
    from kivy.animation import AnimationTransition
    from ._sleep import sleep

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

    # assigning to a local variable might improve the performance
    calculate = _calculate

    if not duration:
        await sleep(0)
        for key, values in properties.items():
            a, b = values
            setattr(target, key, b)
        return

    try:
        time = 0.
        while True:
            time += await sleep(step)

            # calculate progression
            progress = min(1., time / duration)
            t = transition(progress)

            # apply progression on target
            for key, values in properties.items():
                a, b = values
                value = calculate(a, b, t)
                setattr(target, key, value)

            # time to stop ?
            if progress >= 1.:
                return
    finally:
        if force_final_value and progress < 1:
            for key, values in properties.items():
                a, b = values
                setattr(target, key, b)

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


animate = animation  # 'animate' might be a better name
