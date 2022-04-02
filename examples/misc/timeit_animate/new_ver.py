__all__ = ('create_update', )
from functools import partial
from kivy.animation import AnimationTransition
from asynckivy._animation import _update


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
