def test_normaly():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _start_soon

    async def do_nothing():
        pass

    task1 = ak.start_soon(do_nothing())
    task2 = ak.start_soon(do_nothing())
    assert _start_soon._waiting == [task1, task2, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    assert _start_soon._waiting == []
    assert task1.done
    assert task2.done


def test_schedule_another_during_a_scheduled_one():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _start_soon

    task2 = None

    async def job1():
        nonlocal task2
        task2 = ak.start_soon(job2())

    async def job2():
        pass   

    task1 = ak.start_soon(job1())
    assert _start_soon._waiting == [task1, ]
    assert not task1.done
    assert task2 is None
    Clock.tick()
    assert _start_soon._waiting == [task2, ]
    assert task1.done
    assert not task2.done
    Clock.tick()
    assert _start_soon._waiting == []
    assert task1.done
    assert task2.done
