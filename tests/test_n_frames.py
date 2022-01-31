import pytest


def test_one_frame():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.one_frame())
    task2 = ak.start(ak.one_frame())
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    Clock.tick()
    assert _n_frames._waiting == []
    assert task1.done
    assert task2.done


def test_one_frame_cancel():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.one_frame())
    task2 = ak.start(ak.one_frame())
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
    task2.cancel()
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert task2.cancelled
    Clock.tick()
    assert _n_frames._waiting == []
    assert task1.done
    assert task2.cancelled


def test_n_frames():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.n_frames(2))
    task2 = ak.start(ak.n_frames(1))
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


def test_n_frames_cancel():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.n_frames(2))
    task2 = ak.start(ak.n_frames(2))
    assert _n_frames._waiting == [task1._step_coro, task2._step_coro, ]
    assert not task1.done
    assert not task2.done
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


def test_n_frames_zero():
    import asynckivy as ak
    from asynckivy import _n_frames

    task = ak.start(ak.n_frames(0))
    assert _n_frames._waiting == []
    assert task.done


def test_n_frames_negative_number():
    import asynckivy as ak
    from asynckivy import _n_frames

    with pytest.raises(ValueError):
        ak.start(ak.n_frames(-2))
    assert _n_frames._waiting == []
