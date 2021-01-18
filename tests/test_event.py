import pytest


@pytest.fixture(scope='module')
def ed_cls():
    from kivy.event import EventDispatcher
    class ConcreteEventDispatcher(EventDispatcher):
        __events__ = ('on_test', 'on_test2', )
        def on_test(self, *args, **kwargs):
            pass
        def on_test2(self, *args, **kwargs):
            pass
    return ConcreteEventDispatcher


@pytest.fixture()
def ed(ed_cls):
    return ed_cls()


def test_properly_unbound(ed):
    import asynckivy as ak
    async def _test():
        nonlocal state
        state = 'A'
        await ak.event(ed, 'on_test')
        state = 'B'
        await ak.event(ed, 'on_test2')
        state = 'C'
        await ak.event(ed, 'on_test')
        state = 'D'
    state = ''
    ak.start(_test())
    assert state == 'A'
    ed.dispatch('on_test')
    assert state == 'B'
    ed.dispatch('on_test')
    assert state == 'B'
    ed.dispatch('on_test2')
    assert state == 'C'
    ed.dispatch('on_test')
    assert state == 'D'


def test_event_parameter(ed):
    import asynckivy as ak
    async def _test():
        r = await ak.event(ed, 'on_test')
        assert r == (ed, 1, 2, )
        r = await ak.event(ed, 'on_test')
        assert r == (ed, 3, 4, )  # kwarg is ignored
        nonlocal done;done = True
    done = False
    ak.start(_test())
    assert not done
    ed.dispatch('on_test', 1, 2)
    assert not done
    ed.dispatch('on_test', 3, 4, kwarg='A')
    assert done


def test_filter(ed):
    import asynckivy as ak
    async def _test():
        await ak.event(
            ed, 'on_test',
            filter=lambda *args: args == (ed, 3, 4, )
        )
        nonlocal done;done = True
    done = False
    ak.start(_test())
    assert not done
    ed.dispatch('on_test', 1, 2)
    assert not done
    ed.dispatch('on_test', 3, 4)
    assert done


def test_stop_dispatching(ed):
    import asynckivy as ak
    async def _test():
        await ak.event(ed, 'on_test')
        await ak.event(ed, 'on_test', stop_dispatching=True)
        await ak.event(ed, 'on_test')
        nonlocal done;done = True
    done = False
    n = 0
    def increament(*args):
        nonlocal n
        n += 1
    ed.bind(on_test=increament)
    ak.start(_test())
    assert n == 0
    assert not done
    ed.dispatch('on_test')
    assert n == 1
    assert not done
    ed.dispatch('on_test')
    assert n == 1
    assert not done
    ed.dispatch('on_test')
    assert n == 2
    assert done
