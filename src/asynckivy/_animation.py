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
    Animate attibutes of any object. This is basically an async version of :class:`kivy.animation.Animation`.

    .. code-block::

        import types

        obj = types.SimpleNamespace(x=0, size=(200, 300, ))
        await animate(obj, x=100, size=(400, 400))

    :class:`kivy.animation.Animation` requires the object you want to animate to have an attribute named ``uid`` but
    this function does not. Therefore, this one is more broadly applicable than the Kivy's.

    Kivy has two compound animations, :class:`kivy.animation.Sequence` and :class:`kivy.animation.Parallel`.
    You can achieve the same functionality in asynckivy as follows:

    .. code-block::

        from kivy.animation import Animation
        import asynckivy as ak

       def kivy_Sequence(widget):
           anim = Animation(x=100) + Animation(x=0)
           anim.repeat = True
           anim.start(widget)

       async def asynckivy_Sequence(widget):
           while True:
               await ak.animate(widget, x=100)
               await ak.animate(widget, x=0)

       def kivy_Parallel(widget):
           anim = Animation(x=100) & Animation(y=100, duration=2)
           anim.bind(on_complete=lambda *args: print("completed"))
           anim.start(widget)

       async def asynckivy_Parallel(widget):
           await ak.wait_all(
               ak.animate(widget, x=100),
               ak.animate(widget, y=100, duration=2),
           )
           print("completed")
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


def _calculate(a, b, t, isinstance=isinstance, list=list, tuple=tuple, dict=dict, range=range, len=len):
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


def _update(obj, duration, transition, properties, task, p_time, dt, _calculate=_calculate, setattr=setattr):
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
