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

    async def async_fn():
        l = [p async for p in ak.anim_with_ratio(duration=1)]
        assert l == approx([0.3, 0.6, 0.9, 1.2, ])

    task = ak.start(async_fn())
    for __ in range(4):
        sleep_then_tick(.3)
    assert task.finished


def test_ratio_zero_duration(approx, sleep_then_tick):
    import asynckivy as ak

    async def async_fn():
        l = [p async for p in ak.anim_with_ratio(duration=0)]
        assert l == approx([1.0, ])

    task = ak.start(async_fn())
    sleep_then_tick(.1)
    assert task.finished


def test_dt_et_ratio(approx, sleep_then_tick):
    import asynckivy as ak

    async def async_fn():
        dt_result = []
        et_result = []
        progress_result = []
        async for dt, et, p in ak.anim_with_dt_et_ratio(duration=.5):
            dt_result.append(dt)
            et_result.append(et)
            progress_result.append(p)
        assert dt_result == approx([0.2, 0.2, 0.2, ])
        assert et_result == approx([0.2, 0.4, 0.6, ])
        assert progress_result == approx([0.4, 0.8, 1.2, ])

    task = ak.start(async_fn())
    for __ in range(3):
        sleep_then_tick(.2)
    assert task.finished


def test_dt_et_ratio_zero_duration(approx, sleep_then_tick):
    import asynckivy as ak

    async def async_fn():
        l = [v async for v in ak.anim_with_dt_et_ratio(duration=0)]
        # assert l == approx([(0.2, 0.2, 1.0, ), ])  # This doesn't work for some reason.
        assert l[0][0] == approx(0.2)
        assert l[0][1] == approx(0.2)
        assert l[0][2] == approx(1.0)

    task = ak.start(async_fn())
    sleep_then_tick(.2)
    assert task.finished
