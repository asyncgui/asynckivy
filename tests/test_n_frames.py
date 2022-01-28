import pytest


def test_normal():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.n_frames(3))
    task2 = ak.start(ak.n_frames(2))
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    assert _n_frames._waiting == [task1._step_coro, ]
    assert not task1.done
    assert task2.done
    Clock.tick()
    assert _n_frames._waiting == []
    assert task1.done
    assert task2.done


def test_cancel():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.n_frames(3))
    task2 = ak.start(ak.n_frames(3))
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    task2.cancel()
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert task2.cancelled
    Clock.tick()
    assert _n_frames._waiting == [task1._step_coro, ]
    assert not task1.done
    assert task2.cancelled
    Clock.tick()
    assert _n_frames._waiting == []
    assert task1.done
    assert task2.cancelled


def test_zero_frames():
    import asynckivy as ak

    task = ak.start(ak.n_frames(0))
    assert task.done


def test_negative_number_of_frames():
    import asynckivy as ak
    with pytest.raises(ValueError):
        ak.start(ak.n_frames(-2))
