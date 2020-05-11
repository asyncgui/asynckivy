import pytest


def test_gather():
    import asynckivy as ak
    from asynckivy._core import gather
    events = [ak.Event() for __ in range(3)]
    async def _test():
        tasks = await gather(
            (event.wait() for event in events),
            n=2,
        )
        assert tasks[0].done
        assert not tasks[1].done
        assert tasks[2].done
        nonlocal done;done = True
    done = False
    ak.start(_test())
    assert not done
    events[0].set()
    assert not done
    events[0].set()
    assert not done
    events[2].set()
    assert done


class Test_or_:
    def test_normal(self):
        import asynckivy as ak
        events = [ak.Event() for __ in range(3)]
        async def _test():
            tasks = await ak.or_(*(event.wait() for event in events))
            assert not tasks[0].done
            assert tasks[1].done
            assert not tasks[2].done
            nonlocal done;done = True
        done = False
        ak.start(_test())
        assert not done
        events[1].set()
        assert done

    @pytest.mark.parametrize("n_do_nothing", range(1, 4))
    def test_some_coroutines_immediately_end(self, n_do_nothing):
        '''github issue #3'''
        import asynckivy as ak
        async def do_nothing():
            pass
        async def _test():
            tasks = await ak.or_(
                *(do_nothing() for __ in range(n_do_nothing)),
                *(ak.Event().wait() for __ in range(3 - n_do_nothing)),
            )
            for task in tasks[:n_do_nothing]:
                assert task.done
            for task in tasks[n_do_nothing:]:
                assert not task.done
            nonlocal done; done = True
        done = False
        ak.start(_test())
        assert done


class Test_and_:
    def test_normal(self):
        import asynckivy as ak
        events = [ak.Event() for __ in range(3)]
        async def _test():
            tasks = await ak.and_(*(event.wait() for event in events))
            assert tasks[0].done
            assert tasks[1].done
            assert tasks[2].done
            nonlocal done;done = True
        done = False
        ak.start(_test())
        assert not done
        events[1].set()
        assert not done
        events[0].set()
        assert not done
        events[2].set()
        assert done

    @pytest.mark.parametrize("n_coros", range(1, 4))
    def test_all_coroutines_immediately_end(self, n_coros):
        '''github issue #3'''
        import asynckivy as ak
        async def do_nothing():
            pass
        async def _test():
            tasks = await ak.and_(*(do_nothing() for __ in range(n_coros)))
            for task in tasks:
                assert task.done
            nonlocal done; done = True
        done = False
        ak.start(_test())
        assert done


class TestEvent:
    def test_multiple_tasks(self):
        import asynckivy as ak
        e = ak.Event()
        async def _task1():
            await e.wait()
            nonlocal task1_done; task1_done = True
        async def _task2():
            await e.wait()
            nonlocal task2_done; task2_done = True
        task1_done = False
        task2_done = False
        ak.start(_task1())
        ak.start(_task2())
        assert not task1_done
        assert not task2_done
        e.set()
        assert task1_done
        assert task2_done
    def test_set_before_task_starts(self):
        import asynckivy as ak
        e = ak.Event()
        e.set()
        async def _task():
            await e.wait()
            nonlocal done; done = True
        done = False
        ak.start(_task())
        assert done
    def test_clear(self):
        import asynckivy as ak
        e1 = ak.Event()
        e2 = ak.Event()
        async def _task():
            nonlocal task_state
            task_state = 'A'
            await e1.wait()
            task_state = 'B'
            await e2.wait()
            task_state = 'C'
            await e1.wait()
            task_state = 'D'
        task_state = None
        ak.start(_task())
        assert task_state == 'A'
        e1.set()
        assert task_state == 'B'
        e1.clear()
        e2.set()
        assert task_state == 'C'
        e1.set()
        assert task_state == 'D'
