__all__ = (
    'anim_with_dt', 'anim_with_et', 'anim_with_ratio', 'anim_with_dt_et', 'anim_with_dt_et_ratio',
)

from ._sleep import repeat_sleeping


async def anim_with_dt(*, step=0):
    '''
    An async form of :meth:`kivy.clock.Clock.schedule_interval`. The following callback-style code:

    .. code-block::

        def callback(dt):
            print(dt)
            if some_condition:
                return False

        Clock.schedule_interval(callback, 0.1)

    is equivalent to the following async-style code:

    .. code-block::

        async for dt in anim_with_dt(step=0.1):
            print(dt)
            if some_condition:
                break

    .. versionadded:: 0.6.1
    '''
    async with repeat_sleeping(step=step) as sleep:
        while True:
            yield await sleep()


async def anim_with_et(*, step=0):
    '''
    Same as :func:`anim_with_dt` except this one generates the total elapsed time of the loop instead of the elapsed
    time between frames.

    .. code-block::

        timeout = 3.0
        async for et in anim_with_et(...):
            ...
            if et > timeout:
                break

    You can calculate ``et`` by yourself if you want to:

    .. code-block::

        et = 0.
        timeout = 3.0
        async for dt in anim_with_dt(...):
            et += dt
            ...
            if et > timeout:
                break

    which should be as performant as the former.

    .. versionadded:: 0.6.1
    '''
    et = 0.
    async with repeat_sleeping(step=step) as sleep:
        while True:
            et += await sleep()
            yield et


async def anim_with_dt_et(*, step=0):
    '''
    :func:`anim_with_dt` and :func:`anim_with_et` combined.

    .. code-block::

        async for dt, et in anim_with_dt_et(...):
            ...

    .. versionadded:: 0.6.1
    '''
    et = 0.
    async with repeat_sleeping(step=step) as sleep:
        while True:
            dt = await sleep()
            et += dt
            yield dt, et


async def anim_with_ratio(*, duration=1., step=0):
    '''
    Same as :func:`anim_with_et` except this one generates the total progression ratio of the loop.

    .. code-block::

        async for p in anim_with_ratio(duration=3.0):
            print(p * 100, "%")

    If you want to progress at a non-consistant rate, :class:`kivy.animation.AnimationTransition` may be helpful.

    .. code-block::

        from kivy.animation import AnimationTransition

        in_cubic = AnimationTransition.in_cubic

        async for p in anim_with_ratio(duration=3.0):
            p = in_cubic(p)
            print(p * 100, "%")

    .. versionadded:: 0.6.1
    '''
    async with repeat_sleeping(step=step) as sleep:
        if not duration:
            await sleep()
            yield 1.0
            return
        et = 0.
        while et < duration:
            et += await sleep()
            yield et / duration


async def anim_with_dt_et_ratio(*, duration=1., step=0):
    '''
    :func:`anim_with_dt`, :func:`anim_with_et` and :func:`anim_with_ratio` combined.

    .. code-block::

        async for dt, et, p in anim_with_dt_et_ratio(...):
            ...

    .. versionadded:: 0.6.1
    '''
    async with repeat_sleeping(step=step) as sleep:
        if not duration:
            dt = await sleep()
            yield dt, dt, 1.0
            return
        et = 0.
        while et < duration:
            dt = await sleep()
            et += dt
            yield dt, et, et / duration
