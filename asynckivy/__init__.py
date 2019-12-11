__version__ = '0.0.2'
__all__ = (
    'start', 'sleep', 'event', 'thread', 'gather', 'and_', 'or_',
    'animation',
)

import types
import typing
from functools import partial
from kivy.clock import Clock
from inspect import getcoroutinestate, CORO_CLOSED


def start(coro):
    def step_coro(*args, **kwargs):
        try:
            if getcoroutinestate(coro) != CORO_CLOSED:
                coro.send((args, kwargs, ))(step_coro)
        except StopIteration:
            pass

    try:
        coro.send(None)(step_coro)
    except StopIteration:
        pass


@types.coroutine
def sleep(duration):
    # The partial() here looks meaningless. But this is needed in order
    # to avoid weak reference
    args, kwargs = yield lambda step_coro: Clock.schedule_once(
        partial(step_coro), duration)
    return args[0]


@types.coroutine
def event(ed, name, *, filter=None, return_value=None):
    bind_id = None
    step_coro = None

    def bind(step_coro_):
        nonlocal bind_id, step_coro
        bind_id = ed.fbind(name, callback)
        assert bind_id > 0  # check if binding succeeded
        step_coro = step_coro_

    def callback(*args, **kwargs):
        if (filter is not None) and (not filter(*args, **kwargs)):
            return
        ed.unbind_uid(name, bind_id)
        step_coro(*args, **kwargs)
        return return_value

    return (yield bind)[0]


async def thread(func, *args, **kwargs):
    from threading import Thread
    return_value = None
    is_finished = False
    def wrapper(*args, **kwargs):
        nonlocal return_value, is_finished
        return_value = func(*args, **kwargs)
        is_finished = True
    Thread(target=wrapper, args=args, kwargs=kwargs).start()
    while not is_finished:
        await sleep(3)
    return return_value


class Task:
    __slots__ = ('coro', 'done', 'result', 'done_callback')
    def __init__(self, coro, *, done_callback=None):
        self.coro = coro
        self.done = False
        self.result = None
        self.done_callback = done_callback
    async def _run(self):
        self.result = await self.coro
        self.done = True
        if self.done_callback is not None:
            self.done_callback()


@types.coroutine
def gather(coros:typing.Iterable[typing.Coroutine], *, n:int=None) -> typing.Sequence[Task]:
    coros = tuple(coros)
    n_coros_left = n if n is not None else len(coros)
    step_coro = None

    def done_callback():
        nonlocal n_coros_left
        n_coros_left -= 1
        if n_coros_left == 0:
            step_coro()
    tasks = tuple(Task(coro, done_callback=done_callback) for coro in coros)
    for task in tasks:
        start(task._run())

    def callback(step_coro_):
        nonlocal step_coro
        step_coro = step_coro_
    yield callback

    return tasks


async def or_(*coros):
    return await gather(coros, n=1)


async def and_(*coros):
    return await gather(coros)


async def animation(target, **kwargs):
    from time import perf_counter as get_current_time
    from kivy.animation import AnimationTransition

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
    calculate_ = _animation_calculate
    sleep_ = sleep

    if not duration:
        await sleep_(0)
        for key, values in properties.items():
            a, b = values
            setattr(target, key, b)
        return

    start_time = get_current_time()
    while True:
        await sleep_(step)

        # calculate progression
        progress = min(1., (get_current_time() - start_time) / duration)
        t = transition(progress)

        # apply progression on target
        for key, values in properties.items():
            a, b = values
            value = calculate_(a, b, t)
            setattr(target, key, value)

        # time to stop ?
        if progress >= 1.:
            return


def _animation_calculate(a, b, t):
    if isinstance(a, list) or isinstance(a, tuple):
        if isinstance(a, list):
            tp = list
        else:
            tp = tuple
        return tp([_animation_calculate(a[x], b[x], t) for x in range(len(a))])
    elif isinstance(a, dict):
        d = {}
        for x in iterkeys(a):
            if x not in b:
                # User requested to animate only part of the dict.
                # Copy the rest
                d[x] = a[x]
            else:
                d[x] = _animation_calculate(a[x], b[x], t)
        return d
    else:
        return (a * (1. - t)) + (b * t)
