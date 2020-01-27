import pytest


@pytest.fixture(scope='module')
def ed_cls():
    from kivy.event import EventDispatcher
    class ConcreteEventDispatcher(EventDispatcher):
        __events__ = ('on_test', )
        def on_test(self, *args, **kwargs):
            pass
    return ConcreteEventDispatcher


@pytest.fixture()
def ed(ed_cls):
    return ed_cls()


def test_properly_unbound():
    from kivy.uix.button import Button
    import asynckivy as ak
    b = Button()
    async def _test():
        b.text = 'A'
        await ak.event(b, 'on_press')
        b.text = 'B'
        await ak.event(b, 'on_release')
        b.text = 'C'
        await ak.event(b, 'on_press')
        b.text = 'D'
    ak.start(_test())
    assert b.text == 'A'
    b.dispatch('on_press')
    assert b.text == 'B'
    b.dispatch('on_press')
    assert b.text == 'B'
    b.dispatch('on_release')
    assert b.text == 'C'
    b.dispatch('on_press')
    assert b.text == 'D'


def test_event_parameter(ed):
    import asynckivy as ak
    async def _test():
        r = await ak.event(ed, 'on_test')
        assert r == (ed, 1, 2, )
        r = await ak.event(ed, 'on_test')
        assert r == (ed, 3, 4, )  # kwarg is ignored
        nonlocal done
        done = True
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
        nonlocal done
        done = True
    done = False
    ak.start(_test())
    assert not done
    ed.dispatch('on_test', 1, 2)
    assert not done
    ed.dispatch('on_test', 3, 4)
    assert done


def test_return_value(ed):
    import asynckivy as ak
    async def _test():
        await ak.event(ed, 'on_test')
        await ak.event(ed, 'on_test', return_value=True)
        await ak.event(ed, 'on_test')
        nonlocal done
        done = True
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
