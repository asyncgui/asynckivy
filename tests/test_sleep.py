import pytest

p_free = pytest.mark.parametrize("free", (True, False, ))

@p_free
def test_sleep(kivy_runner, free):
    import asynckivy as ak
    kr = kivy_runner

    if free and not hasattr(kivy_runner, 'create_trigger_free'):
        pytest.skip("free-type Clock is not available")
    task = ak.start(ak.sleep_free(.1) if free else ak.sleep(.1))
    assert not task.finished
    kr.advance_a_frame(dt=.05)
    assert not task.finished
    kr.advance_a_frame(dt=.06)
    assert task.finished


@pytest.mark.parametrize('free_to_await', [True, False])
def test_sleep_freq(kivy_runner, free_to_await):
    import asynckivy as ak
    kr = kivy_runner

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
    kr.advance_a_frame(dt=.2)
    assert task_state == 'A'
    assert not task.finished
    kr.advance_a_frame(dt=.5)
    assert task_state == 'B'
    assert not task.finished
    kr.advance_a_frame(dt=.5)
    assert task_state == 'C'
    assert task.finished


@pytest.mark.parametrize('free_to_await', [True, pytest.param(False, marks=pytest.mark.xfail)])
def test_sleep_freq_await_something_else(kivy_runner, free_to_await):
    import asynckivy as ak
    kr = kivy_runner

    async def async_fn():
        async with ak.sleep_freq(step=.8, free_to_await=free_to_await) as sleep:
            await sleep()
            await ak.sleep_forever()  # something else

    task = ak.start(async_fn())
    kr.advance_a_frame(dt=1.)
    kr.advance_a_frame(dt=1.)
    assert not task.cancelled
    task.cancel()
    assert task.cancelled


@p_free
def test_cancel_sleep(kivy_runner, free):
    import asynckivy as ak
    kr = kivy_runner
    TS = ak.TaskState

    if free and not hasattr(kivy_runner, 'create_trigger_free'):
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
    kr.advance_a_frame()
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.FINISHED


def test_cancel_sleep_freq(kivy_runner):
    import asynckivy as ak
    kr = kivy_runner
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
    kr.advance_a_frame()
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.FINISHED
