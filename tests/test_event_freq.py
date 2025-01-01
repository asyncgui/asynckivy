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


def test_properly_cleanuped(ed):
    import asynckivy as ak
    async def async_fn():
        async with ak.event_freq(ed, 'on_test') as on_test:
            await on_test()
            await on_test()
        await ak.sleep_forever()

    task = ak.start(async_fn())
    ed.dispatch('on_test')
    assert not task.finished
    ed.dispatch('on_test')
    assert not task.finished
    ed.dispatch('on_test')
    assert not task.finished
    task._step()
    assert task.finished


def test_event_parameters(ed):
    import asynckivy as ak

    async def async_fn():
        async with ak.event_freq(ed, 'on_test') as on_test:
            assert (ed, 1, 2, ) == await on_test()
            assert (ed, 3, 4, ) == await on_test()  # kwarg is ignored

    task = ak.start(async_fn())
    assert not task.finished
    ed.dispatch('on_test', 1, 2)
    assert not task.finished
    ed.dispatch('on_test', 3, 4, kwarg='A')
    assert task.finished


def test_filter(ed):
    import asynckivy as ak

    async def async_fn():
        async with ak.event_freq(ed, 'on_test', filter=lambda *args: args == (ed, 3, 4, )) as on_test:
            await on_test()

    task = ak.start(async_fn())
    assert not task.finished
    ed.dispatch('on_test', 1, 2)
    assert not task.finished
    ed.dispatch('on_test', 3, 4)
    assert task.finished


def test_stop_dispatching(ed):
    import asynckivy as ak

    called = []

    async def async_fn():
        ed.bind(on_test=lambda *args: called.append(1))
        async with ak.event_freq(ed, 'on_test', stop_dispatching=True) as on_test:
            await on_test()

    task = ak.start(async_fn())
    assert not called
    ed.dispatch('on_test')
    assert not called
    assert task.finished
    ed.dispatch('on_test')
    assert called


def test_cancel(ed):
    import asynckivy as ak

    async def async_fn(ed):
        def filter_func(*args):
            nonlocal called; called = True
            return True
        async with ak.event_freq(ed, 'on_test', filter=filter_func) as on_test:
            await on_test()

    called = False
    task = ak.start(async_fn(ed))
    assert not task.finished
    assert not called
    task.close()
    assert not task.finished
    assert not called
    ed.dispatch('on_test')
    assert not task.finished
    assert not called
