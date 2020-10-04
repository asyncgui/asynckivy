import pytest


def test__get_step_coro():
    import asynckivy as ak
    done = False
    async def job():
        from asynckivy._core import _get_step_coro
        step_coro = await _get_step_coro()
        assert callable(step_coro)
        nonlocal done;done = True
    ak.start(job())
    assert done


def test__get_current_task__without_task():
    import asynckivy as ak
    done = False
    async def job():
        assert await ak.get_current_task() is None
        nonlocal done;done = True
    ak.start(job())
    assert done


def test__get_current_task():
    import asynckivy as ak
    done = False
    async def job():
        assert await ak.get_current_task() is task
        nonlocal done;done = True
    task = ak.Task(job())
    ak.start(task)
    assert done


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
