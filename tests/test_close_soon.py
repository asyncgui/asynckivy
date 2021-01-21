def test_normaly():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _close_soon

    job1_done = False
    job2_done = False

    async def job1():
        try:
            await ak.sleep_forever()
        except GeneratorExit:
            nonlocal job1_done;job1_done = True
            raise

    async def job2():
        try:
            await ak.sleep_forever()
        except GeneratorExit:
            nonlocal job2_done;job2_done = True
            raise

    coro1 = ak.start(job1())
    coro2 = ak.start(job2())
    assert not job1_done
    assert not job2_done
    assert _close_soon._waiting == []
    ak.close_soon(coro1)
    ak.close_soon(coro2)
    assert not job1_done
    assert not job2_done
    assert _close_soon._waiting == [coro1, coro2, ]
    Clock.tick()
    assert job1_done
    assert job2_done
    assert _close_soon._waiting == []


def test_schedule_another_during_a_scheduled_one():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _close_soon

    job1_done = False
    job2_done = False

    async def job1():
        try:
            await ak.sleep_forever()
        except GeneratorExit:
            ak.close_soon(coro2)
            nonlocal job1_done; job1_done = True
            raise

    async def job2():
        try:
            await ak.sleep_forever()
        except GeneratorExit:
            nonlocal job2_done;job2_done = True
            raise

    coro1 = ak.start(job1())
    coro2 = ak.start(job2())
    assert not job1_done
    assert not job2_done
    assert _close_soon._waiting == []
    ak.close_soon(coro1)
    assert not job1_done
    assert not job2_done
    assert _close_soon._waiting == [coro1, ]
    Clock.tick()
    assert job1_done
    assert not job2_done
    assert _close_soon._waiting == [coro2, ]
    Clock.tick()
    assert job1_done
    assert job2_done
    assert _close_soon._waiting == []
