import pytest


@pytest.fixture(scope='module')
def ed_cls():
    from kivy.event import EventDispatcher
    class ConcreteEventDispatcher(EventDispatcher):
        __events__ = ('on_test', )
        def on_test(self, *args, **kwargs):
            pass
    return ConcreteEventDispatcher


def test_gather(ed_cls):
    import asynckivy as ak
    from asynckivy._core import gather
    eds = [ed_cls() for __ in range(3)]
    async def _test():
        tasks = await gather(
            (ak.event(ed, 'on_test') for ed in eds),
            n=2,
        )
        assert tasks[0].done
        assert not tasks[1].done
        assert tasks[2].done
        nonlocal done;done = True
    done = False
    ak.start(_test())
    assert not done
    eds[0].dispatch('on_test')
    assert not done
    eds[0].dispatch('on_test')
    assert not done
    eds[2].dispatch('on_test')
    assert done


def test_gather2(ed_cls):
    import time
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy._core import gather
    eds = [ed_cls() for __ in range(2)]
    async def _test():
        tasks = await gather(
            [
                *(ak.event(ed, 'on_test') for ed in eds),
                ak.sleep(.1),
            ],
            n=2,
        )
        assert tasks[0].done
        assert not tasks[1].done
        assert tasks[2].done
        nonlocal done;done = True
    Clock.tick()
    done = False
    ak.start(_test())
    assert not done
    eds[0].dispatch('on_test')
    assert not done
    eds[0].dispatch('on_test')
    assert not done
    time.sleep(.15)
    Clock.tick()
    assert done


class Test_or_:
    def test_normal(self, ed_cls):
        import asynckivy as ak
        eds = [ed_cls() for __ in range(3)]
        async def _test():
            tasks = await ak.or_(*(ak.event(ed, 'on_test') for ed in eds))
            assert not tasks[0].done
            assert tasks[1].done
            assert not tasks[2].done
            nonlocal done;done = True
        done = False
        ak.start(_test())
        assert not done
        eds[1].dispatch('on_test')
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
                *(ak.sleep_forever() for __ in range(3 - n_do_nothing)),
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
    def test_normal(self, ed_cls):
        import asynckivy as ak
        eds = [ed_cls() for __ in range(3)]
        async def _test():
            tasks = await ak.and_(*(ak.event(ed, 'on_test') for ed in eds))
            assert tasks[0].done
            assert tasks[1].done
            assert tasks[2].done
            nonlocal done;done = True
        done = False
        ak.start(_test())
        assert not done
        eds[1].dispatch('on_test')
        assert not done
        eds[0].dispatch('on_test')
        assert not done
        eds[2].dispatch('on_test')
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
