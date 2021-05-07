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
