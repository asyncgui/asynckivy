import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=0.01)


def test_run_normally(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    async def job(w1, w2):
        async with ak.fade_transition(w1, w2):
            pass

    w1 = SimpleNamespace(opacity=1)
    w2 = SimpleNamespace(opacity=2)
    task = ak.start(job(w1, w2))
    sleep_then_tick(.1)
    assert w1.opacity == approx(.8)
    assert w2.opacity == approx(1.6)
    sleep_then_tick(.4)
    assert w1.opacity == approx(0)
    assert w2.opacity == approx(0)
    sleep_then_tick(.1)
    assert w1.opacity == approx(.2)
    assert w2.opacity == approx(.4)
    sleep_then_tick(.4)
    assert w1.opacity == approx(1)
    assert w2.opacity == approx(2)
    sleep_then_tick(.2)
    assert w1.opacity == 1
    assert w2.opacity == 2
    assert task.finished


def test_cancel(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    async def job(w1, w2):
        async with ak.fade_transition(w1, w2):
            pass

    w1 = SimpleNamespace(opacity=1)
    w2 = SimpleNamespace(opacity=2)
    task = ak.start(job(w1, w2))
    sleep_then_tick(.1)
    assert w1.opacity == approx(.8)
    assert w2.opacity == approx(1.6)
    task.cancel()
    assert w1.opacity == 1
    assert w2.opacity == 2
