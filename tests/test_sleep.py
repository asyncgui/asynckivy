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


@pytest.mark.parametrize('free_to_await', [True, False])
def test_sleep_freq(sleep_then_tick, free_to_await):
    import asynckivy as ak

    async def async_fn():
        nonlocal task_state
        async with ak.sleep_freq(step=.5, free_to_await=free_to_await) as sleep:
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


@pytest.mark.parametrize('free_to_await', [True, pytest.param(False, marks=pytest.mark.xfail)])
def test_sleep_freq_await_something_else(sleep_then_tick, free_to_await):
    import asynckivy as ak

    async def async_fn():
        async with ak.sleep_freq(step=.8, free_to_await=free_to_await) as sleep:
            await sleep()
            await ak.sleep_forever()  # something else

    task = ak.start(async_fn())
    sleep_then_tick(1.)
    sleep_then_tick(1.)
    assert not task.cancelled
    task.cancel()
    assert task.cancelled


@p_free
def test_cancel_sleep(kivy_clock, free):
    import asynckivy as ak
    TS = ak.TaskState

    if free and not hasattr(kivy_clock, 'create_trigger_free'):
        pytest.skip("free-type Clock is not available")

    async def async_fn():
        async with ak.move_on_when(e.wait()):
            await (ak.sleep_free(0) if free else ak.sleep(0))
            pytest.fail()
        await e.wait()

    e = ak.Event()
    task = ak.start(async_fn())
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.STARTED
    kivy_clock.tick()
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.FINISHED


def test_cancel_sleep_freq(kivy_clock):
    import asynckivy as ak
    TS = ak.TaskState

    async def async_fn():
        async with ak.move_on_when(e.wait()):
            async with ak.sleep_freq(step=0) as sleep:
                await sleep()
                pytest.fail()
            pytest.fail()
        await e.wait()

    e = ak.Event()
    task = ak.start(async_fn())
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.STARTED
    kivy_clock.tick()
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.FINISHED
