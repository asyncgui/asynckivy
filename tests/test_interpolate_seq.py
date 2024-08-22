import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)



def test_complete_the_iterations(approx, sleep_then_tick):
    import asynckivy as ak
    values = []

    async def async_fn():
        async for v in ak.interpolate_seq([0, 100], [100, 0], duration=1.0):
            values.extend(v)

    task = ak.start(async_fn())
    assert values == approx([0, 100]) ; values.clear()
    sleep_then_tick(0.3)
    assert values == approx([30, 70]) ; values.clear()
    sleep_then_tick(0.3)
    assert values == approx([60, 40]) ; values.clear()
    sleep_then_tick(0.3)
    assert values == approx([90, 10]) ; values.clear()
    sleep_then_tick(0.3)
    assert values == approx([100, 0]) ; values.clear()
    assert task.finished


@pytest.mark.parametrize('step', [0, 10])
def test_zero_duration(kivy_clock, step):
    import asynckivy as ak
    values = []

    async def async_fn():
        async for v in ak.interpolate_seq([0, 100], [100, 0], duration=0, step=step):
            values.extend(v)

    task = ak.start(async_fn())
    assert values == [0, 100] ; values.clear()
    kivy_clock.tick()
    assert values == [100, 0] ; values.clear()
    assert task.finished


def test_break_during_the_iterations(approx, sleep_then_tick):
    import asynckivy as ak
    values = []

    async def async_fn():
        async for v in ak.interpolate_seq([0, 100], [100, 0], duration=1.0):
            values.extend(v)
            if v[0] > 50:
                break

    task = ak.start(async_fn())
    assert values == approx([0, 100]) ; values.clear()
    sleep_then_tick(.3)
    assert values == approx([30, 70]) ; values.clear()
    sleep_then_tick(.3)
    assert values == approx([60, 40]) ; values.clear()
    assert task.finished
