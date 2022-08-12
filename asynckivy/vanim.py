'''
VAnim: Advanced Animation
=========================

``asynckivy.animate()`` is an imitation of an existing api, ``kivy.animation.Animation``, which is fine because it's
easy to use for the people who are already familiar with Kivy. But it's pretty limited, and is not capable of creating
complex animations. On the contrary, ``vanim`` is low-level, and gives you more control over animations. Let's see how
to use it.

dt (delta time)
---------------

The most low-level api in ``vanim`` would be ``dt``, which is basically an async version of
``Clock.schedule_interval()``. The following callback-based code:

.. code-block:: python

    def callback(dt):
        print(dt)
        if some_condition:
            return False
    Clock.schedule_interval(callback, 0.1)

is equivalent to:

.. code-block:: python

    async for dt in vanim.dt(step=0.1):
        print(dt)
        if some_condition:
            break

et (elapsed time)
-----------------

If you want the total elapsed time of iterations instead of delta time, this is for you.

.. code-block:: python

    timeout = 3.0
    async for et in vanim.et(...):
        ...
        if et > timeout:
            break

You can calculate ``et`` by yourself if you want to:

.. code-block:: python

    et = 0.
    timeout = 3.0
    async for dt in vanim.dt(...):
        et += dt
        ...
        if et > timeout:
            break

which should be as performant as the former.

dt_et
-----

If you want both ``dt`` and ``et``, this is for you.

.. code-block:: python

    timeout = 3.0
    async for dt, et in vanim.dt_et(...):
        ...
        if et > timeout:
            break

progress
--------

If you aren't interested in how much time elapsed, and are only interested in the progression rate, this is for you.

.. code-block:: python

    async for p in vanim.progress(duration=3.0):
        print(p * 100, "%")

If you want non-linear progression, ``AnimationTransition`` may be helpful.

.. code-block:: python

    from kivy.animation import AnimationTransition
    t = AnimationTransition.in_cubic

    async for p in vanim.progress(duration=3.0):
        p = t(p)
        print(p * 100, "%")

dt_et_progress
--------------

Lastly, if you want the all three above, use this.

.. code-block:: python

    async for dt, et, p in vanim.dt_et_progress(duration=3.0):
        ...

The 'free_await' argument
-------------------------

You may notice that the all ``vanim``'s apis take a keyword argument named ``free_await``. If this is False, the
default, you are not allowed to ``await`` during the iterations.

.. code-block:: python

    async for dt in vanim.dt():
        await something  # <- NOT ALLOWED

Only when it's True, you are allowed to do that.

.. code-block:: python

    async for dt in vanim.dt(free_await=True):
        await something  # <- ALLOWED

Iterations may not end in time
------------------------------

This probably doesn't matter as long as the ``step`` is small enough. But in case it's not, be aware of what will
happen.

.. code-block:: python

    async for dt, et, p in vanim.dt_et_progress(duration=2.0, step=0.6):
        print(dt, et, p)

==== ===== =====
 dt   et     p
==== ===== =====
0.6   0.6   0.3
0.6   1.2   0.6
0.6   1.8   0.9
0.6   2.4   1.2
==== ===== =====

Look at the bottom row. ``et`` largely exceeds the ``duration`` and ``p`` largely exceeds 1.0.

Alias
-----

You might dislike abbreviations as they sometimes lower the readability of code. ``vanim`` offers longer names as
well.

* ``dt`` -> ``delta_time``
* ``et`` -> ``elapsed_time``
* ``dt_et`` -> ``delta_time_elapsed_time``
* ``dt_et_progress`` -> ``delta_time_elapsed_time_progress``
'''
__all__ = (
    'dt', 'delta_time', 'et', 'elapsed_time', 'dt_et', 'delta_time_elapsed_time', 'progress', 'dt_et_progress',
    'delta_time_elapsed_time_progress',
)

from asynckivy import repeat_sleeping


async def dt(*, step=0, free_await=False):
    '''read the module doc'''
    async with repeat_sleeping(step, free_await) as sleep:
        while True:
            yield await sleep()


async def et(*, step=0, free_await=False):
    '''read the module doc'''
    et = 0.
    async with repeat_sleeping(step, free_await) as sleep:
        while True:
            dt = await sleep()
            et += dt
            yield et


async def dt_et(*, step=0, free_await=False):
    '''read the module doc'''
    et = 0.
    async with repeat_sleeping(step, free_await) as sleep:
        while True:
            dt = await sleep()
            et += dt
            yield dt, et


async def progress(*, duration=1., step=0, free_await=False):
    '''read the module doc'''
    et = 0.
    async with repeat_sleeping(step, free_await) as sleep:
        while et < duration:
            dt = await sleep()
            et += dt
            yield et / duration


async def dt_et_progress(*, duration=1., step=0, free_await=False):
    '''read the module doc'''
    et = 0.
    async with repeat_sleeping(step, free_await) as sleep:
        while et < duration:
            dt = await sleep()
            et += dt
            yield dt, et, et / duration


# alias
delta_time = dt
elapsed_time = et
delta_time_elapsed_time = dt_et
delta_time_elapsed_time_progress = dt_et_progress
