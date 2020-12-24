import pytest


@pytest.fixture(scope='module')
def touch_cls():
    import weakref
    class Touch:
        __slots__ = ('grab_current', 'grab_list', 'time_end', 'uid', )
        def __init__(self):
            self.grab_current = None
            self.grab_list = []
            self.time_end = -1
            self.uid = 0
        def grab(self, w):
            self.grab_list.append(weakref.ref(w.__self__))
        def ungrab(self, w):
            weak_w = weakref.ref(w.__self__)
            if weak_w in self.grab_list:
                self.grab_list.remove(weak_w)
    return Touch


@pytest.mark.parametrize('n_touch_moves', [0, 1, 10])
def test_a_number_of_on_touch_moves_fired(touch_cls, n_touch_moves):
    from time import perf_counter
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(w, t):
        n = 0
        async for __ in ak.rest_of_touch_moves(w, t):
            n += 1
        assert n == n_touch_moves
        nonlocal done;done = True
        
    done = False
    w = Widget()
    t = touch_cls()
    ak.start(_test(w, t))
    for __ in range(n_touch_moves):
        t.grab_current = None
        w.dispatch('on_touch_move', t)
        t.grab_current = w
        w.dispatch('on_touch_move', t)
    t.grab_current = None
    w.dispatch('on_touch_up', t)
    t.grab_current = w
    w.dispatch('on_touch_up', t)
    assert done


def test_break_during_a_for_loop(touch_cls):
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(w, t):
        import weakref
        nonlocal n_touch_moves
        weak_w = weakref.ref(w)
        assert weak_w not in t.grab_list
        async for __ in ak.rest_of_touch_moves(w, t):
            assert weak_w in t.grab_list
            n_touch_moves += 1
            if n_touch_moves == 2:
                break
        assert weak_w not in t.grab_list
        await ak.event(w, 'on_touch_up')
        nonlocal done;done = True

    n_touch_moves = 0
    done = False
    w = Widget()
    t = touch_cls()
    ak.start(_test(w, t))
    for expected in (1, 2, 2, ):
        t.grab_current = None
        w.dispatch('on_touch_move', t)
        t.grab_current = w
        w.dispatch('on_touch_move', t)
        assert n_touch_moves == expected
        assert not done
    t.grab_current = None
    w.dispatch('on_touch_up', t)
    t.grab_current = w
    w.dispatch('on_touch_up', t)
    assert n_touch_moves == 2
    assert done


@pytest.mark.parametrize(
    'eat_touch, expectation', [
        (True, [0, 0, 0, ], ),
        (False, [1, 2, 1, ], ),
    ])
def test_eat_touch_events(touch_cls, eat_touch, expectation):
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(parent, t):
        async for __ in ak.rest_of_touch_moves(
                parent, t, eat_touch=eat_touch):
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


@pytest.mark.parametrize('actually_ended', (True, False))
def test_the_touch_that_might_already_ended(touch_cls, actually_ended):
    import time
    from kivy.clock import Clock
    from kivy.uix.widget import Widget
    import asynckivy as ak
    from asynckivy.exceptions import MotionEventAlreadyEndedError
    Clock.tick()

    async def job(w, t):
        if actually_ended:
            with pytest.raises(MotionEventAlreadyEndedError):
                async for __ in ak.rest_of_touch_moves(w, t):
                    pass
        else:
            async for __ in ak.rest_of_touch_moves(w, t):
                pass
        nonlocal done;done = True

    done = False
    w = Widget()
    t = touch_cls()
    t.time_end = 1  # something other than -1
    ak.start(job(w, t))

    if actually_ended:
        time.sleep(0)
        Clock.tick()
    else:
        t.grab_current = None
        w.dispatch('on_touch_up', t)
        t.grab_current = w
        w.dispatch('on_touch_up', t)
    assert done
