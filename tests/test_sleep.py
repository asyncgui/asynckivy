import pytest

p_free = pytest.mark.parametrize("free", (True, False, ))

@p_free
def test_sleep(kivy_clock, sleep_then_tick, free):
    import asynckivy as ak

    if free and not hasattr(kivy_clock, 'create_trigger_free'):
        pytest.skip("free-type Clock is not available")
    task = ak.start(ak.sleep_free(.1) if free else ak.sleep(.1))
    assert not task.finished
    sleep_then_tick(.05)
    assert not task.finished
    sleep_then_tick(.06)
    assert task.finished


@pytest.mark.parametrize('free_await', (False, True))
def test_repeat_sleeping(sleep_then_tick, free_await):
    import asynckivy as ak

    async def async_fn():
        nonlocal task_state
        async with ak.repeat_sleeping(step=.5, free_await=free_await) as sleep:
            task_state = 'A'
            await sleep()
            task_state = 'B'
            await sleep()
            task_state = 'C'

    task_state = None
    task = ak.start(async_fn())
    sleep_then_tick(.2)
    assert task_state == 'A'
    assert not task.finished
    sleep_then_tick(.5)
    assert task_state == 'B'
    assert not task.finished
    sleep_then_tick(.5)
    assert task_state == 'C'
    assert task.finished


def test_free_awaitが真の時は勝手にtaskを再開しない(sleep_then_tick):
    import asynckivy as ak

    async def async_fn():
        async with ak.repeat_sleeping(step=0, free_await=True) as sleep:
            await ak.sleep_forever()

    task = ak.start(async_fn())
    sleep_then_tick(.1)
    assert not task.finished


@p_free
def test_sleep_cancel(kivy_clock, free):
    import asynckivy as ak

    if free and not hasattr(kivy_clock, 'create_trigger_free'):
        pytest.skip("free-type Clock is not available")

    async def async_fn(ctx):
        async with ak.open_cancel_scope() as scope:
            ctx['scope'] = scope
            ctx['state'] = 'A'
            await (ak.sleep_free(0) if free else ak.sleep(0))
            pytest.fail()
        ctx['state'] = 'B'
        await ak.sleep_forever()
        ctx['state'] = 'C'

    ctx = {}
    task = ak.start(async_fn(ctx))
    assert ctx['state'] == 'A'
    ctx['scope'].cancel()
    assert ctx['state'] == 'B'
    kivy_clock.tick()
    assert ctx['state'] == 'B'
    task._step()
    assert ctx['state'] == 'C'


@pytest.mark.parametrize('free_await', (False, True))
def test_cancel_repeat_sleeping(kivy_clock, free_await):
    import asynckivy as ak

    async def async_fn(ctx):
        async with ak.open_cancel_scope() as scope:
            ctx['scope'] = scope
            ctx['state'] = 'A'
            async with ak.repeat_sleeping(step=0, free_await=free_await) as sleep:
                await sleep()
            pytest.fail()
        ctx['state'] = 'B'
        await ak.sleep_forever()
        ctx['state'] = 'C'

    ctx = {}
    task = ak.start(async_fn(ctx))
    assert ctx['state'] == 'A'
    ctx['scope'].cancel()
    assert ctx['state'] == 'B'
    kivy_clock.tick()
    assert ctx['state'] == 'B'
    task._step()
    assert ctx['state'] == 'C'


def test_cancel_repeat_sleeping2(kivy_clock):
    import asynckivy as ak

    async def async_fn(ctx):
        async with ak.repeat_sleeping(step=0, free_await=True) as sleep:
            async with ak.open_cancel_scope() as scope:
                ctx['scope'] = scope
                ctx['state'] = 'A'
                await sleep()
                pytest.fail()
            ctx['state'] = 'B'
            await ak.sleep_forever()
            ctx['state'] = 'C'

    ctx = {}
    task = ak.start(async_fn(ctx))
    assert ctx['state'] == 'A'
    ctx['scope'].cancel()
    assert ctx['state'] == 'B'
    kivy_clock.tick()
    assert ctx['state'] == 'B'
    task._step()
    assert ctx['state'] == 'C'
