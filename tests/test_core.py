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
    eds = [ed_cls() for __ in range(3)]
    async def _test():
        tasks = await ak.gather(
            (ak.event(ed, 'on_test') for ed in eds),
            n=2,
        )
        assert tasks[0].done
        assert not tasks[1].done
        assert tasks[2].done
        nonlocal done
        done = True
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
    eds = [ed_cls() for __ in range(2)]
    async def _test():
        tasks = await ak.gather(
            [
                *(ak.event(ed, 'on_test') for ed in eds),
                ak.sleep(.1),
            ],
            n=2,
        )
        assert tasks[0].done
        assert not tasks[1].done
        assert tasks[2].done
        nonlocal done
        done = True
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


def test_or_(ed_cls):
    import asynckivy as ak
    eds = [ed_cls() for __ in range(3)]
    async def _test():
        tasks = await ak.or_(*(ak.event(ed, 'on_test') for ed in eds))
        assert not tasks[0].done
        assert tasks[1].done
        assert not tasks[2].done
        nonlocal done
        done = True
    done = False
    ak.start(_test())
    assert not done
    eds[1].dispatch('on_test')
    assert done


def test_and_(ed_cls):
    import asynckivy as ak
    eds = [ed_cls() for __ in range(3)]
    async def _test():
        tasks = await ak.and_(*(ak.event(ed, 'on_test') for ed in eds))
        assert tasks[0].done
        assert tasks[1].done
        assert tasks[2].done
        nonlocal done
        done = True
    done = False
    ak.start(_test())
    assert not done
    eds[1].dispatch('on_test')
    assert not done
    eds[0].dispatch('on_test')
    assert not done
    eds[2].dispatch('on_test')
    assert done
