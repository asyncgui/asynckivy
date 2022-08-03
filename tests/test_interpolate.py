import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


def test_complete_the_iteration(approx, sleep_then_tick):
    import asynckivy as ak

    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100)]
        assert l == approx([0, 30, 60, 90, 100])

    task = ak.start(job())
    for __ in range(4):
        sleep_then_tick(.3)
    assert task.done


def test_break_during_the_iteration(approx, sleep_then_tick):
    import asynckivy as ak

    async def job():
        l = []
        async for v in ak.interpolate(start=0, end=100):
            l.append(v)
            if v > 50:
                break
        assert l == approx([0, 30, 60, ])

    task = ak.start(job())
    for __ in range(2):
        sleep_then_tick(.3)
    assert task.done


def test_zero_duration(approx):
    import asynckivy as ak

    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100, d=0)]
        assert l == approx([0, 100])

    task = ak.start(job())
    assert task.done
