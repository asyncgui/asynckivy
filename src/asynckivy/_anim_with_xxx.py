from ._sleep import sleep_freq


async def anim_with_ratio(*, base, step=0):
    '''
    Returns an async iterator that yields the elapsed time since the start of the iteration, divided by ``base``.

    .. code-block::

        async for p in anim_with_ratio(base=3):
            print(p)

    The code above is equivalent to the following:

    .. code-block::

        async with sleep_freq() as sleep:
            base = 3
            total_elapsed_time = 0.
            while True:
                total_elapsed_time += await sleep()
                p = total_elapsed_time / base
                print(p)

    Use :class:`kivy.animation.AnimationTransition` for non-linear curves.

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
    async with sleep_freq(step=step) as sleep:
        et = 0.
        while True:
            et += await sleep()
            yield et / base
