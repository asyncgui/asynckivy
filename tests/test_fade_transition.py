import pytest


def test_invalid_argument():
    import asynckivy as ak
    async def job():
        async with ak.fade_transition(unknown=True):
            pass
    with pytest.raises(ValueError):
        ak.start(job())


def test_run_normally(ready_to_sleep):
    from functools import partial
    from kivy.uix.widget import Widget
    import asynckivy as ak
    approx = partial(pytest.approx, rel=0.01)

    async def job(w1, w2):
        async with ak.fade_transition(w1, w2):
            pass

    w1 = Widget(opacity=1)
    w2 = Widget(opacity=2)
    sleep = ready_to_sleep()
    task = ak.start(job(w1, w2))
    sleep(.1)
    assert w1.opacity == approx(.8)
    assert w2.opacity == approx(1.6)
    sleep(.4)
    assert w1.opacity == pytest.approx(0, abs=0.01)
    assert w2.opacity == pytest.approx(0, abs=0.01)
    sleep(.1)
    assert w1.opacity == approx(.2)
    assert w2.opacity == approx(.4)
    sleep(.4)
    assert w1.opacity == approx(1)
    assert w2.opacity == approx(2)
    sleep(.2)
    assert w1.opacity == 1
    assert w2.opacity == 2
    assert task.done


def test_cancel(ready_to_sleep):
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def job(w1, w2):
        async with ak.fade_transition(w1, w2):
            pass

    w1 = Widget(opacity=1)
    w2 = Widget(opacity=2)
    sleep = ready_to_sleep()
    task = ak.start(job(w1, w2))
    sleep(.1)
    assert w1.opacity != 1
    assert w2.opacity != 2
    task.cancel()
    assert w1.opacity == 1
    assert w2.opacity == 2
