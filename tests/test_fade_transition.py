import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=0.01)


def test_run_normally(approx, kivy_runner):
    from types import SimpleNamespace
    import asynckivy as ak
    kr = kivy_runner

    async def job(w1, w2):
        async with ak.fade_transition(w1, w2):
            pass

    w1 = SimpleNamespace(opacity=1)
    w2 = SimpleNamespace(opacity=2)
    task = ak.start(job(w1, w2))
    kr.advance_a_frame(dt=.1)
    assert w1.opacity == approx(.8)
    assert w2.opacity == approx(1.6)
    kr.advance_a_frame(dt=.4)
    assert w1.opacity == approx(0)
    assert w2.opacity == approx(0)
    kr.advance_a_frame(dt=.1)
    assert w1.opacity == approx(.2)
    assert w2.opacity == approx(.4)
    kr.advance_a_frame(dt=.4)
    assert w1.opacity == approx(1)
    assert w2.opacity == approx(2)
    kr.advance_a_frame(dt=.2)
    assert w1.opacity == 1
    assert w2.opacity == 2
    assert task.finished


def test_cancel(approx, kivy_runner):
    from types import SimpleNamespace
    import asynckivy as ak
    kr = kivy_runner

    async def job(w1, w2):
        async with ak.fade_transition(w1, w2):
            pass

    w1 = SimpleNamespace(opacity=1)
    w2 = SimpleNamespace(opacity=2)
    task = ak.start(job(w1, w2))
    kr.advance_a_frame(dt=.1)
    assert w1.opacity == approx(.8)
    assert w2.opacity == approx(1.6)
    task.cancel()
    assert w1.opacity == 1
    assert w2.opacity == 2
