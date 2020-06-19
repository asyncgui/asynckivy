import pytest


@pytest.fixture(scope='module')
def touch_cls():
    class Touch:
        __slots__ = ('grab_current', )
        def __init__(self):
            self.grab_current = None
        def grab(self, w):
            self.grab_current = w
        def ungrab(self, w):
            pass
    return Touch


@pytest.mark.parametrize('n_touch_move', [0, 1, 10])
def test_a_number_of_on_touch_move_fired(touch_cls, n_touch_move):
    from time import perf_counter
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(w, t):
        from asynckivy import rest_of_touch_moves 
        n = 0
        async for __ in rest_of_touch_moves(w, t):
            n += 1
        assert n == n_touch_move
        nonlocal done;done = True
        
    done = False
    w = Widget()
    t = touch_cls()
    ak.start(_test(w, t))
    for __ in range(n_touch_move):
        w.dispatch('on_touch_move', t)
    w.dispatch('on_touch_up', t)
    assert done


def test_break_during_a_for_loop(touch_cls):
    from time import perf_counter
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(w, t):
        from asynckivy import rest_of_touch_moves, event
        nonlocal n
        async for __ in rest_of_touch_moves(w, t):
            n += 1
            if n == 2:
                break
        await event(w, 'on_touch_up')
        nonlocal done;done = True

    n = 0
    done = False
    w = Widget()
    t = touch_cls()
    ak.start(_test(w, t))
    w.dispatch('on_touch_move', t)
    assert n == 1
    assert not done
    w.dispatch('on_touch_move', t)
    assert n == 2
    assert not done
    w.dispatch('on_touch_move', t)
    assert n == 2
    assert not done
    w.dispatch('on_touch_up', t)
    assert n == 2
    assert done
