__all__ = ('animate', )
import types
from functools import partial
from kivy.clock import Clock
from kivy.animation import AnimationTransition
from asynckivy import sleep, sleep_forever
from ._simple_ver import _calculate


async def animate(target, **kwargs):
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
        for key, values in properties.items():
            a, b = values
            setattr(target, key, b)
        return

    try:
        ctx = {
            'target': target,
            'time': 0.,
            'duration': duration,
            'transition': transition,
            'properties': properties,
        }
        await _save_step_coro(ctx)
        clock_event = Clock.schedule_interval(partial(_update, ctx), step)
        await sleep_forever()
    except GeneratorExit:
        if force_final_value:
            for key, values in properties.items():
                a, b = values
                setattr(target, key, b)
        raise
    finally:
        clock_event.cancel()


@types.coroutine
def _save_step_coro(ctx):
    yield lambda step_coro: (ctx.__setitem__('step_coro', step_coro), step_coro())


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
