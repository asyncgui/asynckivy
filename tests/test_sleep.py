import pytest

def test_sleep():
    import time
    from kivy.clock import Clock
    import asynckivy as ak

    Clock.tick()
    task = ak.start(ak.sleep(.1))
    assert not task.done
    Clock.tick()
    assert not task.done
    time.sleep(.07)
    Clock.tick()
    assert not task.done
    time.sleep(.07)
    Clock.tick()
    assert task.done


def test_sleep_free():
    import time
    from kivy.clock import Clock
    import asynckivy as ak

    if not hasattr(Clock, 'create_trigger_free'):
        pytest.skip("free-type Clock is not available")
    Clock.tick()
    task = ak.start(ak.sleep_free(.1))
    assert not task.done
    Clock.tick()
    assert not task.done
    time.sleep(.07)
    Clock.tick()
    assert not task.done
    time.sleep(.07)
    Clock.tick()
    assert task.done


@pytest.mark.parametrize('free_await', (False, True))
def test_repeat_sleeping(free_await):
    import time
    from kivy.clock import Clock
    import asynckivy as ak

    async def async_fn():
        nonlocal task_state
        async with ak.repeat_sleeping(.5, free_await=free_await) as sleep:
            task_state = 'A'
            await sleep()
            task_state = 'B'
            await sleep()
            task_state = 'C'

    task_state = None
    Clock.tick()
    task = ak.start(async_fn())
    time.sleep(.2)
    Clock.tick()
    assert task_state == 'A'
    assert not task.done
    time.sleep(.5)
    Clock.tick()
    assert task_state == 'B'
    assert not task.done
    time.sleep(.5)
    Clock.tick()
    assert task_state == 'C'
    assert task.done


def test_create_sleep():
    import time
    from kivy.clock import Clock
    import asynckivy as ak

    async def _task():
        nonlocal task_state
        sleep = await ak.create_sleep(.5)
        task_state = 'A'
        await sleep()
        task_state = 'B'
        await sleep()
        task_state = 'C'

    task_state = None
    Clock.tick()
    ak.start(_task())
    time.sleep(.2)
    Clock.tick()
    assert task_state == 'A'
    time.sleep(.5)
    Clock.tick()
    assert task_state == 'B'
    time.sleep(.5)
    Clock.tick()
    assert task_state == 'C'
