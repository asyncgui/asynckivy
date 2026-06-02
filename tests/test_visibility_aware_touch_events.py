import pytest


TREE = """
Widget:
    Widget:
        id: clipper
        pos: 0, 0
        size: 100, 100
        Widget:
            id: target
            pos: 50, 0
            size: 100, 100
            Widget:
                id: child
"""

def not_colliding(widget, touch):
    return not widget.collide_point(*touch.pos)


@pytest.fixture()
def tree(kivy_runner):
    tree = kivy_runner.builder.load_string(TREE)
    tree.ids.clipper.bind(
        on_touch_down=not_colliding,
        on_touch_move=not_colliding,
        on_touch_up=not_colliding,
    )
    kivy_runner.window.add_widget(tree)
    kivy_runner.advance_a_frame()
    return tree


@pytest.mark.parametrize("stop_dispatching", [True, False])
@pytest.mark.parametrize("x_list, expect", [
    ([20, 30], [False, False]),
    ([60, 80], [True, True]),
    ([30, 60], [False, True]),
    ([60, 30], [True, False]),
])
def test_full_consumption(tree, stop_dispatching, x_list, expect):
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w, t):
        result = []
        async with ak.visibility_aware_touch_events(w, t, stop_dispatching=stop_dispatching) as on_touch_move:
            while True:
                result.append(await on_touch_move())
        return result

    t = UnitTestTouch(0, 0)
    task = ak.start(async_fn(tree.ids.target, t))
    t.touch_down()
    for x in x_list:
        t.touch_move(x, 50)
    t.touch_up()
    assert task.result == expect


@pytest.mark.parametrize("stop_dispatching", [True, False])
@pytest.mark.parametrize("x_list, expect", [
    ([20, 30, 90], [False, False]),
    ([60, 80, 90], [True, True]),
    ([30, 60, 90], [False, True]),
    ([60, 30, 90], [True, False]),
])
def test_partial_consumption(tree, stop_dispatching, x_list, expect):
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w, t):
        result = []
        async with ak.visibility_aware_touch_events(w, t, stop_dispatching=stop_dispatching) as on_touch_move:
            while True:
                result.append(await on_touch_move())
                if len(result) == 2:
                    break
        return result

    t = UnitTestTouch(0, 0)
    task = ak.start(async_fn(tree.ids.target, t))
    for x in x_list:
        t.touch_move(x, 50)
    assert task.result == expect


@pytest.mark.parametrize("stop_dispatching", [True, False])
@pytest.mark.parametrize("x_list, expect", [
    ([20, 30], {"move": 2, "up": 1, }),
    ([60, 80], {"move": 2, "up": 1, }),
    ([30, 60], {"move": 2, "up": 1, }),
    ([60, 30], {"move": 2, "up": 1, }),
    ([90, 120], {"move": 1, "up": 0, }),
    ([120, 90], {"move": 1, "up": 1, }),
    ([120, 140], {"move": 0, "up": 0, }),
])
def test_child_event_counts(tree, stop_dispatching, x_list, expect):
    from kivy.tests.common import UnitTestTouch
    import asynckivy as ak

    async def async_fn(w, t):
        async with ak.visibility_aware_touch_events(w, t, stop_dispatching=stop_dispatching) as on_touch_move:
            while True:
                await on_touch_move()

    event_counts = {"move": 0, "up": 0, }
    def on_touch_move(w, t):
        assert t.grab_current is None
        event_counts["move"] += 1
    def on_touch_up(w, t):
        assert t.grab_current is None
        event_counts["up"] += 1
    tree.ids.child.bind(
        on_touch_move=on_touch_move,
        on_touch_up=on_touch_up,
    )

    t = UnitTestTouch(0, 0)
    task = ak.start(async_fn(tree.ids.target, t))
    t.touch_down()
    for x in x_list:
        t.touch_move(x, 50)
    t.touch_up()
    if stop_dispatching:
        assert event_counts == {"move": 0, "up": 0, }
    else:
        assert event_counts == expect
    assert task.finished
