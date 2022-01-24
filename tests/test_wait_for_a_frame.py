def test_normaly():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _wait_for_a_frame
    from asynckivy._wait_for_a_frame import wait_for_a_frame

    async def job1():
        await wait_for_a_frame()
        await wait_for_a_frame()
        await wait_for_a_frame()

    async def job2():
        await wait_for_a_frame()
        await wait_for_a_frame()

    task1 = ak.start(job1())
    task2 = ak.start(job2())
    assert _wait_for_a_frame._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    assert _wait_for_a_frame._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    assert _wait_for_a_frame._waiting == [task1._step_coro, ]
    assert not task1.done
    assert task2.done
    Clock.tick()
    assert _wait_for_a_frame._waiting == []
    assert task1.done
    assert task2.done


def test_cancel():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _wait_for_a_frame
    from asynckivy._wait_for_a_frame import wait_for_a_frame

    async def job():
        await wait_for_a_frame()
        await wait_for_a_frame()
        await wait_for_a_frame()

    task1 = ak.start(job())
    task2 = ak.start(job())
    assert _wait_for_a_frame._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    task2.cancel()
    assert _wait_for_a_frame._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert task2.cancelled
    Clock.tick()
    assert _wait_for_a_frame._waiting == [task1._step_coro, ]
    assert not task1.done
    assert task2.cancelled
    Clock.tick()
    assert _wait_for_a_frame._waiting == []
    assert task1.done
    assert task2.cancelled
