def test_normaly():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _start_soon

    job1_done = False
    async def job1():
        nonlocal job1_done;job1_done = True    
    job2_done = False
    async def job2():
        nonlocal job2_done;job2_done = True    

    coro1 = ak.start_soon(job1())
    coro2 = ak.start_soon(job2())
    assert _start_soon._waiting == [coro1, coro2, ]
    assert not job1_done
    assert not job2_done
    Clock.tick()
    assert _start_soon._waiting == []
    assert job1_done
    assert job2_done


def test_schedule_another_during_a_scheduled_one():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _start_soon

    coro2 = None

    job1_done = False
    async def job1():
        nonlocal coro2
        coro2 = ak.start_soon(job2())
        nonlocal job1_done;job1_done = True    
    job2_done = False
    async def job2():
        nonlocal job2_done;job2_done = True    

    coro1 = ak.start_soon(job1())
    assert _start_soon._waiting == [coro1, ]
    assert not job1_done
    assert not job2_done
    Clock.tick()
    assert _start_soon._waiting == [coro2, ]
    assert job1_done
    assert not job2_done
    Clock.tick()
    assert _start_soon._waiting == []
    assert job1_done
    assert job2_done
