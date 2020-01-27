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
@pytest.mark.parametrize('version', ['complicated', 'simple', ])
def test_number_of_on_touch_move_fired(touch_cls, n_touch_move, version):
    from time import perf_counter
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(w, t):
        from asynckivy import _all_touch_moves 
        all_touch_moves = getattr(_all_touch_moves, f'_all_touch_moves_{version}_ver')
        n = 0
        async for __ in all_touch_moves(w, t):
            n += 1
        assert n == n_touch_move
        nonlocal done
        done = True
        
    done = False
    w = Widget()
    t = touch_cls()
    ak.start(_test(w, t))
    for __ in range(n_touch_move):
        w.dispatch('on_touch_move', t)
    w.dispatch('on_touch_up', t)
    assert done


def test_complicated_one_is_faster_than_simple_one(touch_cls):
    from time import perf_counter
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def time_a_touch(w, t, all_touch_moves):
        start = perf_counter()
        async for __ in all_touch_moves(w, t):
            pass
        return perf_counter() - start

    async def time_multiple_touches(w, t, all_touch_moves, n):
        time_list = [
            (await time_a_touch(w, t, all_touch_moves))
            for __ in range(n)
        ]
        return sum(time_list)

    async def _test(w, t, n):
        from asynckivy._all_touch_moves import (
            _all_touch_moves_complicated_ver as c_ver,
            _all_touch_moves_simple_ver as s_ver,
        )
        c_ver_result = await time_multiple_touches(w, t, c_ver, n)
        s_ver_result = await time_multiple_touches(w, t, s_ver, n)
        assert c_ver_result < s_ver_result
        nonlocal done
        done = True
        
    done = False
    n = 100
    n_touch_move = 100
    w = Widget()
    t = touch_cls()
    ak.start(_test(w, t, n))
    for __ in range(n * 2):  # * 2 because needs for both c_ver and s_ver
        for __ in range(n_touch_move):
            w.dispatch('on_touch_move', t)
        w.dispatch('on_touch_up', t)
    assert done


@pytest.mark.parametrize('version', ['complicated', 'simple', ])
def test_break_during_a_for_loop(touch_cls, version):
    from time import perf_counter
    from kivy.uix.widget import Widget
    import asynckivy as ak

    async def _test(w, t):
        from asynckivy import _all_touch_moves, event
        nonlocal n, done
        all_touch_moves = getattr(_all_touch_moves, f'_all_touch_moves_{version}_ver')
        async for __ in all_touch_moves(w, t):
            n += 1
            if n == 2:
                break
        await event(w, 'on_touch_up')
        done = True

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
