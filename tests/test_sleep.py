import pytest

def test_sleep(sleep_then_tick):
    import asynckivy as ak

    task = ak.start(ak.sleep(.1))
    assert not task.done
    sleep_then_tick(.05)
    assert not task.done
    sleep_then_tick(.06)
    assert task.done


def test_sleep_free(sleep_then_tick):
    from kivy.clock import Clock
    import asynckivy as ak

    if not hasattr(Clock, 'create_trigger_free'):
        pytest.skip("free-type Clock is not available")
    task = ak.start(ak.sleep_free(.1))
    assert not task.done
    sleep_then_tick(.05)
    assert not task.done
    sleep_then_tick(.06)
    assert task.done


@pytest.mark.parametrize('free_await', (False, True))
def test_repeat_sleeping(sleep_then_tick, free_await):
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
    task = ak.start(async_fn())
    sleep_then_tick(.2)
    assert task_state == 'A'
    assert not task.done
    sleep_then_tick(.5)
    assert task_state == 'B'
    assert not task.done
    sleep_then_tick(.5)
    assert task_state == 'C'
    assert task.done
