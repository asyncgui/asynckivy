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
    Returns an async iterator that yields the elapsed time since the start of the iteration.

    .. code-block::

        async for et in anim_with_et(...):
            print(et)

    The code above is equivalent to the following:

    .. code-block::

        et = 0.
        async for dt in anim_with_dt(...):
            et += dt
            print(et)

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


async def anim_with_ratio(*, base, step=0):
    '''
    Returns an async iterator that yields the elapsed time since the start of the iteration, divided by ``base``.

    .. code-block::

        async for p in anim_with_ratio(base=3):
            print(p)

    The code above is equivalent to the following:

    .. code-block::

        base = 3
        async for et in anim_with_et():
            p = et / base
            print(p)

    If you want non-linear ratio values, you may find :class:`kivy.animation.AnimationTransition` helpful.

    .. code-block::

        from kivy.animation import AnimationTransition

        in_cubic = AnimationTransition.in_cubic

        async for p in anim_with_ratio(base=...):
            p = in_cubic(p)
            print(p)

    .. versionadded:: 0.6.1

    .. versionchanged:: 0.7.0

        The ``duration`` parameter was replaced with ``base``.
        The loop no longer ends on its own.
    '''
    async with repeat_sleeping(step=step) as sleep:
        et = 0.
        while True:
            et += await sleep()
            yield et / base


async def anim_with_dt_et_ratio(*, base, step=0):
    '''
    :func:`anim_with_dt`, :func:`anim_with_et` and :func:`anim_with_ratio` combined.

    .. code-block::

        async for dt, et, p in anim_with_dt_et_ratio(...):
            ...

    .. versionadded:: 0.6.1

    .. versionchanged:: 0.7.0
        The ``duration`` parameter was replaced with ``base``.
        The loop no longer ends on its own.
    '''
    async with repeat_sleeping(step=step) as sleep:
        et = 0.
        while True:
            dt = await sleep()
            et += dt
            yield dt, et, et / base
