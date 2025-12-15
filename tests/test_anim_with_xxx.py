import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=0.004)


def test_ratio(approx, sleep_then_tick):
    import asynckivy as ak

    values = []
    async def async_fn():
        async for p in ak.anim_with_ratio(base=3.0):
            values.append(p)

    task = ak.start(async_fn())
    for __ in range(4):
        sleep_then_tick(.3)
    assert values == approx([0.1, 0.2, 0.3, 0.4, ])
    assert task.state is ak.TaskState.STARTED
    task.cancel()


def test_ratio_zero_base(kivy_clock):
    import asynckivy as ak

    async def async_fn():
        with pytest.raises(ZeroDivisionError):
            async for p in ak.anim_with_ratio(base=0):
                pass

    task = ak.start(async_fn())
    kivy_clock.tick()
    assert task.finished
