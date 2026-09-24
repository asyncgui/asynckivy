import pytest


def test_sleep(kivy_runner):
    import asynckivy as ak
    kr = kivy_runner

    task = ak.start(ak.sleep(.1))
    assert not task.finished
    kr.advance_a_frame(dt=.05)
    assert not task.finished
    kr.advance_a_frame(dt=.06)
    assert task.finished


def test_sleep_freq(kivy_runner):
    import asynckivy as ak
    kr = kivy_runner

    async def async_fn():
        nonlocal task_state
        with ak.sleep_freq(step=.5) as sleep:
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


def test_sleep_freq_await_something_else(kivy_runner):
    import asynckivy as ak
    kr = kivy_runner

    async def async_fn():
        with ak.sleep_freq(step=.8) as sleep:
            await sleep()
            await ak.sleep_forever()  # something else

    task = ak.start(async_fn())
    kr.advance_a_frame(dt=1.)
    kr.advance_a_frame(dt=1.)
    assert not task.cancelled
    task.cancel()
    assert task.cancelled


def test_cancel_sleep(kivy_runner):
    import asynckivy as ak
    kr = kivy_runner
    TS = ak.TaskState

    async def async_fn():
        async with ak.move_on_when(e.wait()):
            await (ak.sleep(0))
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
            with ak.sleep_freq(step=0) as sleep:
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
