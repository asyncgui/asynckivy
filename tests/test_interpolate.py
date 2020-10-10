import pytest


@pytest.fixture(autouse=True)
def unlimit_maxfps(monkeypatch):
    from kivy.clock import Clock
    monkeypatch.setattr(Clock, '_max_fps', 0)


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


def test_complete_iteration(approx):
    from .test_animation import Clock
    import asynckivy as ak

    done = False
    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100, step=.3)]
        assert l == approx([0, 30, 60, 90, 100])
        nonlocal done;done = True
    clock = Clock()
    ak.start(job())
    for __ in range(130):
        clock.sleep(.01)
    assert done


def test_break_during_iteration(approx):
    from .test_animation import Clock
    import asynckivy as ak

    done = False
    async def job():
        l = []
        async for v in ak.interpolate(start=0, end=100, step=.3):
            l.append(v)
            if v > 50:
                break
        assert l == approx([0, 30, 60, ])
        await ak.sleep_forever()
        nonlocal done;done = True
    clock = Clock()
    coro = ak.start(job())
    for __ in range(130):
        clock.sleep(.01)
    assert not done
    with pytest.raises(StopIteration):
        coro.send(None)
    assert done


def test_zero_duration(approx):
    import asynckivy as ak

    done = False
    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100, step=.3, d=0)]
        assert l == approx([0, 100])
        nonlocal done;done = True
    ak.start(job())
    assert done
