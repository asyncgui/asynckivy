import pytest


@pytest.fixture(scope='module')
def frog_cls():
    from kivy.event import EventDispatcher
    from kivy.properties import NumericProperty

    class Frog(EventDispatcher):
        __events__ = ('on_jump', )
        n_jumped = NumericProperty(0)

        def on_jump(self, distance=0):
            self.n_jumped += 1

    return Frog


@pytest.fixture()
def frog(frog_cls):
    return frog_cls()


def test_simple_use(frog):
    from asynckivy import suppress_event

    assert frog.n_jumped == 0
    with suppress_event(frog, 'on_jump'):
        frog.dispatch('on_jump')
    assert frog.n_jumped == 0
    frog.dispatch('on_jump')
    assert frog.n_jumped == 1
    with suppress_event(frog, 'on_jump'):
        frog.dispatch('on_jump')
    assert frog.n_jumped == 1
    frog.dispatch('on_jump')
    assert frog.n_jumped == 2


def test_filter(frog):
    from asynckivy import suppress_event

    with suppress_event(frog, 'on_jump', filter=lambda __, distance: distance > 1):
        frog.dispatch('on_jump', distance=2)
        assert frog.n_jumped == 0
        frog.dispatch('on_jump', distance=0)
        assert frog.n_jumped == 1
        frog.dispatch('on_jump', distance=2)
        assert frog.n_jumped == 1
        frog.dispatch('on_jump', distance=0)
        assert frog.n_jumped == 2

    frog.dispatch('on_jump', distance=2)
    assert frog.n_jumped == 3


def test_bind_a_callback_after_entering(frog):
    from asynckivy import suppress_event

    called = False

    def callback(frog, distance=0):
        nonlocal called; called = True

    with suppress_event(frog, 'on_jump'):
        frog.bind(on_jump=callback)
        frog.dispatch('on_jump')
        assert called
        assert frog.n_jumped == 0
