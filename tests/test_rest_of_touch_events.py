import pytest


@pytest.mark.parametrize('n_touch_moves', [0, 1, 10])
def test_count_a_number_of_on_touch_move_events(kivy_runner, n_touch_moves):
    from kivy.uix.widget import Widget
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w, t):
        n = 0
        async for __ in ak.rest_of_touch_events(w, t):
            n += 1
        return n

    w = Widget()
    kivy_runner.window.add_widget(w)
    kivy_runner.advance_a_frame()
    t = UnitTestTouch(0, 0)
    task = ak.start(async_fn(w, t))
    t.touch_down()
    for __ in range(n_touch_moves):
        t.touch_move(0, 0)
    t.touch_up()
    assert task.result == n_touch_moves


def test_break_during_the_iteration(kivy_runner):
    from kivy.uix.widget import Widget
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w, t):
        import weakref
        nonlocal n_touch_moves
        weak_w = weakref.ref(w)
        assert weak_w not in t.grab_list
        async for __ in ak.rest_of_touch_events(w, t):
            assert weak_w in t.grab_list
            n_touch_moves += 1
            if n_touch_moves == 2:
                break
        assert weak_w not in t.grab_list
        await ak.event(w, 'on_touch_up')

    n_touch_moves = 0
    w = Widget()
    kivy_runner.window.add_widget(w)
    kivy_runner.advance_a_frame()
    t = UnitTestTouch(0, 0)
    task = ak.start(async_fn(w, t))
    for expected in (1, 2, 2, ):
        t.touch_move(0, 0)
        assert n_touch_moves == expected
        assert not task.finished
    t.touch_up()
    assert n_touch_moves == 2
    assert task.finished


@pytest.mark.parametrize(
    'stop_dispatching, expectation', [
        (True, [0, 0, 0, ], ),
        (False, [1, 2, 1, ], ),
    ])
def test_stop_dispatching(kivy_runner, stop_dispatching, expectation):
    from kivy.uix.widget import Widget
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(parent, t):
        async for __ in ak.rest_of_touch_events(parent, t, stop_dispatching=stop_dispatching):
            pass

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
    kivy_runner.window.add_widget(parent)
    kivy_runner.advance_a_frame()
    t = UnitTestTouch(0, 0)
    task = ak.start(async_fn(parent, t))

    for i in range(2):
        t.touch_move(0, 0)
        assert n_touches['move'] == expectation[i]
    t.touch_up()
    assert n_touches['up'] == expectation[2]
    assert task.finished
