import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=0.004)


def test_dt(approx, sleep_then_tick):
    import asynckivy as ak

    async def async_fn(result: list):
        async for dt in ak.anim_with_dt():
            result.append(dt)

    result = []
    durations = [.2, .5, .1, ]
    task = ak.start(async_fn(result))
    for d in durations:
        sleep_then_tick(d)
    assert result == approx(durations)
    task.cancel()


def test_et(approx, sleep_then_tick):
    from itertools import accumulate
    import asynckivy as ak

    async def async_fn(result: list):
        async for et in ak.anim_with_et():
            result.append(et)

    result = []
    durations = (.2, .5, .1, )
    task = ak.start(async_fn(result))
    for d in durations:
        sleep_then_tick(d)
    assert result == approx(list(accumulate(durations)))
    task.cancel()


def test_dt_et(approx, sleep_then_tick):
    from itertools import accumulate
    import asynckivy as ak

    async def async_fn(dt_result: list, et_result: list):
        async for dt, et in ak.anim_with_dt_et():
            dt_result.append(dt)
            et_result.append(et)

    # 'pytest.approx()' doesn't support nested lists/tuples so we put 'dt' and 'et' separately.
    dt_result = []
    et_result = []
    durations = (.2, .5, .1, )
    task = ak.start(async_fn(dt_result, et_result))
    for d in durations:
        sleep_then_tick(d)
    assert dt_result == approx(list(durations))
    assert et_result == approx(list(accumulate(durations)))
    task.cancel()


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


def test_dt_et_ratio(approx, sleep_then_tick):
    import asynckivy as ak

    dt_values = []
    et_values = []
    p_values = []

    async def async_fn():
        async for dt, et, p in ak.anim_with_dt_et_ratio(base=.5):
            dt_values.append(dt)
            et_values.append(et)
            p_values.append(p)

    task = ak.start(async_fn())
    for __ in range(4):
        sleep_then_tick(.2)
    assert dt_values == approx([0.2, 0.2, 0.2, 0.2, ])
    assert et_values == approx([0.2, 0.4, 0.6, 0.8, ])
    assert p_values == approx([0.4, 0.8, 1.2, 1.6, ])
    assert task.state is ak.TaskState.STARTED
    task.cancel()


def test_dt_et_ratio_zero_base(kivy_clock):
    import asynckivy as ak

    async def async_fn():
        with pytest.raises(ZeroDivisionError):
            async for dt, et, p in ak.anim_with_dt_et_ratio(base=0):
                pass

    task = ak.start(async_fn())
    kivy_clock.tick()
    assert task.finished
