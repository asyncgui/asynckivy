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
        pytest.skip("free-type Clock is not avaiable")
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


def test_n_frames():
    from kivy.clock import Clock
    import asynckivy as ak

    task = ak.start(ak.n_frames(3))
    Clock.tick()
    assert not task.done
    Clock.tick()
    assert not task.done
    Clock.tick()
    assert task.done


def test_n_frames_zero():
    import asynckivy as ak

    task = ak.start(ak.n_frames(0))
    assert task.done


def test_n_frames_negative_number():
    import asynckivy as ak
    with pytest.raises(ValueError):
        ak.start(ak.n_frames(-2))
