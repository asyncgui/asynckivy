import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


def test_complete_the_iteration(approx, kivy_runner):
    import asynckivy as ak
    kr = kivy_runner

    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100)]
        assert l == approx([0, 30, 60, 90, 100])

    task = ak.start(job())
    for __ in range(4):
        kr.advance_a_frame(dt=.3)
    assert task.finished


def test_break_during_the_iteration(approx, kivy_runner):
    import asynckivy as ak
    kr = kivy_runner

    async def job():
        l = []
        async for v in ak.interpolate(start=0, end=100):
            l.append(v)
            if v > 50:
                break
        assert l == approx([0, 30, 60, ])

    task = ak.start(job())
    for __ in range(2):
        kr.advance_a_frame(dt=.3)
    assert task.finished


def test_zero_duration(approx, kivy_runner):
    import asynckivy as ak
    kr = kivy_runner

    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100, duration=0)]
        assert l == approx([0, 100])

    task = ak.start(job())
    kr.advance_a_frame(dt=.1)
    assert task.finished
