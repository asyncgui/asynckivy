__all__ = ('animate', )
from functools import partial
from kivy.clock import Clock
from kivy.animation import AnimationTransition
from asynckivy import sleep, sleep_forever


async def animate(target, **kwargs):
    '''
    animate
    =======

    An asynchronous version of ``kivy.animation.Animation``.

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

    One notable difference is ``force_final_value``, which ensures the
    final-value of the animation to be applied even when the animation is
    cancelled.

    .. code-block:: python

       import asynckivy as ak

       widget.x = 0
       coro = ak.start(ak.animate(widget, x=100, force_final_value=True))
       coro.close()  # cancels immediately
       assert widget.x == 100  # but the final-value is applied

    I believe this is useful when you want an animation to be skippable.

    .. code-block:: python

       import asynckivy as ak

       async def skippable_animation(label):
           # can be skipped by 'on_touch_down'.
           tasks = await ak.or_(
               ak.animate(label, x=100, force_final_value=True),
               ak.event(label, 'on_touch_down')
           )
           tasks[0].cancel()

    Sequence and Parallel
    ---------------------

    Kivy has two compound animations: ``Sequence`` and ``Parallel``.
    You can achive the same functionality in asynckivy as follows.

    .. code-block:: python

       def kivy_way_of_doing_sequential_animation(widget):
           anim = Animation(x=100) + Animation(x=0)
           anim.repeat = True
           anim.start(widget)

       async def asynckivy_way_of_doing_sequential_animation(widget):
           while True:
               await ak.animate(widget, x=100)
               await ak.animate(widget, x=0)

       def kivy_way_of_doing_parallel_animation(widget):
           anim = Animation(x=100) & Animation(y=100, d=2)
           anim.start(widget)

       async def asynckivy_way_of_doing_parallel_animation(widget):
           await ak.and_(
               ak.animate(widget, x=100),
               ak.animate(widget, y=100, d=2),
           )
    '''
    from asyncgui import get_step_coro
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
            'step_coro': await get_step_coro(),
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
