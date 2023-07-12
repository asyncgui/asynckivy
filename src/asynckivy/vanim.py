'''
:func:`asynckivy.animate` is an imitation of an existing api, :class:`kivy.animation.Animation`,
which is fine because it's easy to use for the people who are already familiar with Kivy.
The problem is ... it's a pretty specialized api because:

* It can only animate attributes. Sometimes, I just need the value without actually assigning it to an attribute.
  (:func:`asynckivy.interpolate` already solved this problem, though.)
* It can only interpolate between **two** values. What if you want to do it with more than two values,
  like Bézier Curve?

On the contrary, ``vanim`` is low-level.
In fact, it's presumptuous to classify it as an animation api.
All it does is calculating elapsed-time or progression-rate or both.
What to do with those values is all up to you.

That concludes the overview.
Now, let's dive into each individual api.

dt (delta time)
---------------

The most low-level api in ``vanim`` is ``dt``, which is basically the async form of
:meth:`kivy.clock.Clock.schedule_interval`. The following callback-based code:

.. code-block::

    def callback(dt):
        print(dt)
        if some_condition:
            return False
    Clock.schedule_interval(callback, 0.1)

is equivalent to:

.. code-block::

    async for dt in vanim.dt(step=0.1):
        print(dt)
        if some_condition:
            break

et (elapsed time)
-----------------

If you want the total elapsed time of iterations instead of delta time, this is for you.

.. code-block::

    timeout = 3.0
    async for et in vanim.et(...):
        ...
        if et > timeout:
            break

You can calculate ``et`` by yourself if you want to:

.. code-block::

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

.. code-block::

    timeout = 3.0
    async for dt, et in vanim.dt_et(...):
        ...
        if et > timeout:
            break

progress
--------

If you aren't interested in how much time elapsed, and are only interested in the progression rate, this is for you.

.. code-block::

    async for p in vanim.progress(duration=3.0):
        print(p * 100, "%")

If you want non-linear progression, :class:`kivy.animation.AnimationTransition` may be helpful.

.. code-block::

    from kivy.animation import AnimationTransition

    transition = AnimationTransition.in_cubic

    async for p in vanim.progress(duration=3.0):
        p = transition(p)
        print(p * 100, "%")

dt_et_progress
--------------

Lastly, if you want the all three above, use this.

.. code-block::

    async for dt, et, p in vanim.dt_et_progress(duration=3.0):
        ...

The ``free_await`` parameter
----------------------------

You might notice that all the ``vanim``'s apis take a keyword argument named ``free_await``.
This works exactly the same as the :class:`asynckivy.repeat_sleeping` 's.

Iterations may not end in time
------------------------------

This probably doesn't matter as long as the ``step`` is small enough. But in case it's not, be aware of what will
happen.

.. code-block::

    async for dt, et, p in vanim.dt_et_progress(duration=2.0, step=0.6):
        print(dt, et, p)

==== ========= =========
 dt     et         p
==== ========= =========
0.6     0.6       0.3
0.6     1.2       0.6
0.6     1.8       0.9
0.6   **2.4**   **1.2**
==== ========= =========

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
    'dt', 'delta_time',
    'et', 'elapsed_time',
    'dt_et', 'delta_time_elapsed_time',
    'progress',
    'dt_et_progress', 'delta_time_elapsed_time_progress',
)

from asynckivy import repeat_sleeping


async def dt(*, step=0, free_await=False):
    async with repeat_sleeping(step=step, free_await=free_await) as sleep:
        while True:
            yield await sleep()


async def et(*, step=0, free_await=False):
    et = 0.
    async with repeat_sleeping(step=step, free_await=free_await) as sleep:
        while True:
            et += await sleep()
            yield et


async def dt_et(*, step=0, free_await=False):
    et = 0.
    async with repeat_sleeping(step=step, free_await=free_await) as sleep:
        while True:
            dt = await sleep()
            et += dt
            yield dt, et


async def progress(*, duration=1., step=0, free_await=False):
    et = 0.
    async with repeat_sleeping(step=step, free_await=free_await) as sleep:
        while et < duration:
            et += await sleep()
            yield et / duration


async def dt_et_progress(*, duration=1., step=0, free_await=False):
    et = 0.
    async with repeat_sleeping(step=step, free_await=free_await) as sleep:
        while et < duration:
            dt = await sleep()
            et += dt
            yield dt, et, et / duration


# alias
delta_time = dt
elapsed_time = et
delta_time_elapsed_time = dt_et
delta_time_elapsed_time_progress = dt_et_progress
