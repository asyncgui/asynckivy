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


@pytest.mark.parametrize(
    'eats_touch_move, eats_touch_up, expectation', [
        (True, True, [0, 0, 0, ], ),
        (True, False, [0, 0, 1, ], ),
        (False, True, [1, 2, 0, ], ),
        (False, False, [1, 2, 1, ], ),
    ])
def test_eat_touch_events(touch_cls, eats_touch_move, eats_touch_up, expectation):
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(parent, t):
        from asynckivy import rest_of_touch_moves 
        async for __ in rest_of_touch_moves(
                parent, t,
                eats_touch_move=eats_touch_move,
                eats_touch_up=eats_touch_up):
            pass
        nonlocal done;done = True

    done = False

    n_touches = {'move': 0, 'up': 0, }
    def on_touch_move(*args):
        n_touches['move'] += 1
    def on_touch_up(*args):
        n_touches['up'] += 1

    parent = Widget()
    child = Widget(
        on_touch_move=on_touch_move,
        on_touch_up=on_touch_up,
    )
    parent.add_widget(child)
    t = touch_cls()
    ak.start(_test(parent, t))

    for i in range(2):
        t.grab_current = None
        parent.dispatch('on_touch_move', t)
        t.grab_current = parent
        parent.dispatch('on_touch_move', t)
        assert n_touches['move'] == expectation[i]
    t.grab_current = None
    parent.dispatch('on_touch_up', t)
    t.grab_current = parent
    parent.dispatch('on_touch_up', t)
    assert n_touches['up'] == expectation[2]
    assert done
