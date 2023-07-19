import pytest


@pytest.mark.parametrize('n', (1, 2, ))
def test_consecutive_touches(n):
    from kivy.uix.widget import Widget
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w):
        for __ in range(n):
            __, touch = await ak.event(w, 'on_touch_down')
            await ak.touch_up_event(w, touch)

    w = Widget()
    t = UnitTestTouch(0, 0)
    task = ak.start(async_fn(w))
    for __ in range(n):
        assert not task.finished
        t.grab_current = None
        w.dispatch('on_touch_down', t)
        assert not task.finished
        t.grab_current = None
        w.dispatch('on_touch_up', t)
        assert not task.finished
        t.grab_current = w
        w.dispatch('on_touch_up', t)
    assert task.finished


def test_multiple_touches_at_the_same_time():
    from kivy.uix.widget import Widget
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w):
        __, touch = await ak.event(w, 'on_touch_down')
        await ak.touch_up_event(w, touch)

    w = Widget()
    t = UnitTestTouch(0, 0)
    t2 = UnitTestTouch(0, 0)
    task = ak.start(async_fn(w))

    assert not task.finished
    t.grab_current = None
    w.dispatch('on_touch_down', t)

    assert not task.finished
    t2.grab_current = None
    w.dispatch('on_touch_up', t2)
    assert not task.finished
    t2.grab_current = w
    w.dispatch('on_touch_up', t2)

    assert not task.finished
    t.grab_current = None
    w.dispatch('on_touch_up', t)
    assert not task.finished
    t.grab_current = w
    w.dispatch('on_touch_up', t)

    assert task.finished


@pytest.mark.parametrize('timeout', (.2, 1.))
@pytest.mark.parametrize('actually_ended', (True, False))
def test_a_touch_that_might_have_already_ended(sleep_then_tick, timeout, actually_ended):
    from contextlib import nullcontext
    from kivy.uix.widget import Widget
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w, t):
        with pytest.raises(ak.MotionEventAlreadyEndedError) if actually_ended else nullcontext():
            await ak.touch_up_event(w, t, timeout=timeout)

    w = Widget()
    t = UnitTestTouch(0, 0)
    t.time_end = 1  # something other than -1
    task = ak.start(async_fn(w, t))

    if actually_ended:
        sleep_then_tick(timeout)
    else:
        t.grab_current = None
        w.dispatch('on_touch_up', t)
        t.grab_current = w
        w.dispatch('on_touch_up', t)
    assert task.finished
