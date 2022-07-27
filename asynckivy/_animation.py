__all__ = ('animate', )
from functools import partial
from kivy.clock import Clock
from kivy.animation import AnimationTransition
from asyncgui import get_step_coro
from asynckivy import sleep_forever


async def animate(target, **kwargs):  # noqa:C901
    '''
    animate
    =======

    An async version of ``kivy.animation.Animation``.

    Usage
    -----

    .. code-block:: python

       import asynckivy as ak

       async def some_async_func(widget):
           # case #1: start an animation and wait for its completion
           await ak.animate(widget, x=100, d=2, s=.2, t='in_cubic')

       # case #2: start an animation but not wait for its completion
       ak.start(ak.animate(widget, ...))

    Difference from kivy.animation.Animation
    ----------------------------------------

    ``kivy.animation.Animation`` requires the object you wanna animate to
    have an attribute named ``uid`` but ``asynckivy`` does not. When you have
    an object like this:

    .. code-block:: python

       class MyClass: pass
       obj = MyClass()
       obj.value = 100

    you already can animate it by ``asynckivy.animate(obj, value=200)``.
    Therefore, ``asynckivy.animate()`` is more broadly applicable than
    ``kivy.animation.Animation``.

    Sequence and Parallel
    ---------------------

    Kivy has two compound animations: ``Sequence`` and ``Parallel``.
    You can achieve the same functionality in asynckivy as follows:

    .. code-block:: python

       def kivy_Sequence(widget):
           anim = Animation(x=100) + Animation(x=0)
           anim.repeat = True
           anim.start(widget)

       async def asynckivy_Sequence(widget):
           while True:
               await ak.animate(widget, x=100)
               await ak.animate(widget, x=0)

       def kivy_Parallel(widget):
           anim = Animation(x=100) & Animation(y=100, d=2)
           anim.start(widget)
           anim.bind(on_complete=lambda *args: print("completed"))

       async def asynckivy_Parallel(widget):
           await ak.and_(
               ak.animate(widget, x=100),
               ak.animate(widget, y=100, d=2),
           )
           print("completed")
    '''
    duration = kwargs.pop('d', kwargs.pop('duration', 1.))
    transition = kwargs.pop('t', kwargs.pop('transition', 'linear'))
    step = kwargs.pop('s', kwargs.pop('step', 0))
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

    try:
        clock_event = Clock.schedule_interval(
            partial(_update, target, duration, transition, properties, await get_step_coro(), [0., ]),
            step,
        )
        await sleep_forever()
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


def _update(target, duration, transition, properties, step_coro, p_time, dt, _calculate=_calculate, setattr=setattr):
    time = p_time[0] + dt
    p_time[0] = time

    # calculate progression
    progress = min(1., time / duration)
    t = transition(progress)

    # apply progression on target
    for key, values in properties.items():
        a, b = values
        value = _calculate(a, b, t)
        setattr(target, key, value)

    # time to stop ?
    if progress >= 1.:
        step_coro()
        return False
