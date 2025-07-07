__all__ = ('anim_attrs', 'anim_attrs_abbr', )
import types
from functools import partial
import kivy.clock
from kivy.animation import AnimationTransition
import asyncgui


def _update(setattr, zip, min, obj, duration, transition, anim_params, task, p_time, dt):
    time = p_time[0] + dt
    p_time[0] = time

    # calculate progression
    progress = min(1., time / duration)
    t = transition(progress)

    # apply progression on obj
    for attr_name, org_value, slope, is_seq in anim_params:
        if is_seq:
            new_value = [
                slope_elem * t + org_elem
                for org_elem, slope_elem in zip(org_value, slope)
            ]
            setattr(obj, attr_name, new_value)
        else:
            setattr(obj, attr_name, slope * t + org_value)

    # time to stop ?
    if progress >= 1.:
        task._step()
        return False


_update = partial(_update, setattr, zip, min)


@types.coroutine
def _anim_attrs(
        obj, duration, step, transition, animated_properties,
        getattr=getattr, isinstance=isinstance, tuple=tuple, str=str, partial=partial, native_seq_types=(tuple, list),
        zip=zip, Clock=kivy.clock.Clock, AnimationTransition=AnimationTransition,
        _update=_update, _current_task=asyncgui._current_task, _sleep_forever=asyncgui._sleep_forever, /):
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)

    # get current values & calculate slopes
    anim_params = [
        (
            org_value := getattr(obj, attr_name),
            is_seq := isinstance(org_value, native_seq_types),
            (
                org_value := tuple(org_value),
                slope := [goal_elem - org_elem for goal_elem, org_elem in zip(goal_value, org_value)],
            ) if is_seq else (slope := goal_value - org_value),
        ) and (attr_name, org_value, slope, is_seq, )
        for attr_name, goal_value in animated_properties.items()
    ]

    try:
        clock_event = Clock.schedule_interval(
            partial(_update, obj, duration, transition, anim_params, (yield _current_task)[0][0], [0., ]),
            step,
        )
        yield _sleep_forever
    finally:
        clock_event.cancel()


def anim_attrs(obj, *, duration=1.0, step=0, transition=AnimationTransition.linear, **animated_properties):
    '''
    Animates attibutes of any object.

    .. code-block::

        import types

        obj = types.SimpleNamespace(x=0, size=(200, 300))
        await anim_attrs(obj, x=100, size=(400, 400))

    .. warning::

        Unlike :class:`kivy.animation.Animation`, this one does not support dictionary-type and nested-sequence.

        .. code-block::

            await anim_attrs(obj, pos_hint={'x': 1.})  # not supported
            await anim_attrs(obj, nested_sequence=[[10, 20, ]])  # not supported

            await anim_attrs(obj, color=(1, 0, 0, 1), pos=(100, 200))  # OK

    .. versionadded:: 0.6.1
    .. versionchanged:: 0.9.0
        The ``output_seq_type`` parameter was removed.
    '''
    return _anim_attrs(obj, duration, step, transition, animated_properties)


def anim_attrs_abbr(obj, *, d=1.0, s=0, t=AnimationTransition.linear, **animated_properties):
    '''
    :func:`anim_attrs` cannot animate attributes named ``step``, ``duration`` and ``transition`` but this one can.

    .. versionadded:: 0.6.1
    .. versionchanged:: 0.9.0
        The ``output_seq_type`` parameter was removed.
    '''
    return _anim_attrs(obj, d, s, t, animated_properties)
