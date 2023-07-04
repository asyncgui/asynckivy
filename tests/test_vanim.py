import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=0.004)


@pytest.mark.parametrize('free_await', (False, True))
def test_dt(approx, sleep_then_tick, free_await):
    import asynckivy as ak

    async def async_fn(result: list):
        from asynckivy import vanim
        async for dt in vanim.dt(free_await=free_await):
            result.append(dt)

    result = []
    durations = [.2, .5, .1, ]
    task = ak.start(async_fn(result))
    for d in durations:
        sleep_then_tick(d)
    assert result == approx(durations)
    task.cancel()


@pytest.mark.parametrize('free_await', (False, True))
def test_et(approx, sleep_then_tick, free_await):
    from itertools import accumulate
    import asynckivy as ak

    async def async_fn(result: list):
        from asynckivy import vanim
        async for et in vanim.et(free_await=free_await):
            result.append(et)

    result = []
    durations = (.2, .5, .1, )
    task = ak.start(async_fn(result))
    for d in durations:
        sleep_then_tick(d)
    assert result == approx(list(accumulate(durations)))
    task.cancel()


@pytest.mark.parametrize('free_await', (False, True))
def test_dt_et(approx, sleep_then_tick, free_await):
    from itertools import accumulate
    import asynckivy as ak

    async def async_fn(dt_result: list, et_result: list):
        from asynckivy import vanim
        async for dt, et in vanim.dt_et(free_await=free_await):
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


@pytest.mark.parametrize('free_await', (False, True))
def test_progress(approx, sleep_then_tick, free_await):
    import asynckivy as ak

    async def async_fn():
        from asynckivy import vanim
        l = [p async for p in vanim.progress(duration=1, free_await=free_await)]
        assert l == approx([0.3, 0.6, 0.9, 1.2, ])

    task = ak.start(async_fn())
    for __ in range(4):
        sleep_then_tick(.3)
    assert task.finished


@pytest.mark.parametrize('free_await', (False, True))
def test_dt_et_progress(approx, sleep_then_tick, free_await):
    import asynckivy as ak

    async def async_fn():
        from asynckivy import vanim
        dt_result = []
        et_result = []
        progress_result = []
        async for dt, et, p in vanim.dt_et_progress(duration=.5, free_await=free_await):
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
