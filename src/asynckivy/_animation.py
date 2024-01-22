__all__ = ('animate', )
import typing as T
import types
from functools import partial
from kivy.clock import Clock
from kivy.animation import AnimationTransition
from asyncgui import _sleep_forever, _current_task


@types.coroutine
def animate(obj, *, duration=1.0, step=0, transition=AnimationTransition.linear, **animated_properties) -> T.Awaitable:
    '''
    Animates attibutes of any object. This is basically an async form of :class:`kivy.animation.Animation`.

    .. code-block::

        import types

        obj = types.SimpleNamespace(x=0, size=(200, 300, ))
        await animate(obj, x=100, size=(400, 400))

    Kivy has two compound animations, :class:`kivy.animation.Sequence` and :class:`kivy.animation.Parallel`.
    You can achieve the same functionality as them in asynckivy as follows:

    .. code-block::

        import asynckivy as ak

        async def sequential_animation(widget):
            await ak.animate(widget, x=100)
            await ak.animate(widget, x=0)

        async def parallel_animation(widget):
            await ak.wait_all(
                ak.animate(widget, x=100),
                ak.animate(widget, y=100, duration=2),
            )

    .. deprecated:: 0.6.1

        This will be removed before version 1.0.0.
        Use :func:`asynckivy.anim_attrs` or :func:`asynckivy.anim_attrs_abbr` instead.
    '''
    if not duration:
        for key, value in animated_properties.items():
            setattr(obj, key, value)
        return
    if isinstance(transition, str):
        transition = getattr(AnimationTransition, transition)

    # get current values
    properties = {}
    for key, value in animated_properties.items():
        original_value = getattr(obj, key)
        if isinstance(original_value, (tuple, list)):
            original_value = original_value[:]
        elif isinstance(original_value, dict):
            original_value = original_value.copy()
        properties[key] = (original_value, value)

    try:
        clock_event = Clock.schedule_interval(
            partial(_update, obj, duration, transition, properties, (yield _current_task)[0][0], [0., ]),
            step,
        )
        yield _sleep_forever
    finally:
        clock_event.cancel()


def _calculate(isinstance, list, tuple, dict, range, len, a, b, t):
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


def _update(setattr, _calculate, obj, duration, transition, properties, task, p_time, dt):
    time = p_time[0] + dt
    p_time[0] = time

    # calculate progression
    progress = min(1., time / duration)
    t = transition(progress)

    # apply progression on obj
    for key, values in properties.items():
        a, b = values
        value = _calculate(a, b, t)
        setattr(obj, key, value)

    # time to stop ?
    if progress >= 1.:
        task._step()
        return False


_calculate = partial(_calculate, isinstance, list, tuple, dict, range, len)
_update = partial(_update, setattr, _calculate)
