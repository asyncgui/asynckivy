import pytest


def test_one_frame():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.one_frame())
    task2 = ak.start(ak.one_frame())
    assert _n_frames._waiting_tasks == [task1, task2, ]
    assert not task1.finished
    assert not task2.finished
    Clock.tick()
    assert _n_frames._waiting_tasks == []
    assert task1.finished
    assert task2.finished


def test_one_frame_cancel():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.one_frame())
    task2 = ak.start(ak.one_frame())
    assert _n_frames._waiting_tasks == [task1, task2, ]
    assert not task1.finished
    assert not task2.finished
    task2.cancel()
    assert _n_frames._waiting_tasks == [task1, None, ]
    assert not task1.finished
    assert task2.cancelled
    Clock.tick()
    assert _n_frames._waiting_tasks == []
    assert task1.finished
    assert task2.cancelled


def test_n_frames():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.n_frames(2))
    task2 = ak.start(ak.n_frames(1))
    assert _n_frames._waiting_tasks == [task1, task2, ]
    assert not task1.finished
    assert not task2.finished
    Clock.tick()
    assert _n_frames._waiting_tasks == [task1, ]
    assert not task1.finished
    assert task2.finished
    Clock.tick()
    assert _n_frames._waiting_tasks == []
    assert task1.finished
    assert task2.finished


def test_n_frames_cancel():
    from kivy.clock import Clock
    import asynckivy as ak
    from asynckivy import _n_frames

    task1 = ak.start(ak.n_frames(2))
    task2 = ak.start(ak.n_frames(2))
    assert _n_frames._waiting_tasks == [task1, task2, ]
    assert not task1.finished
    assert not task2.finished
    task2.cancel()
    assert _n_frames._waiting_tasks == [task1, None, ]
    assert not task1.finished
    assert task2.cancelled
    Clock.tick()
    assert _n_frames._waiting_tasks == [task1, ]
    assert not task1.finished
    assert task2.cancelled
    Clock.tick()
    assert _n_frames._waiting_tasks == []
    assert task1.finished
    assert task2.cancelled


def test_n_frames_zero():
    import asynckivy as ak
    from asynckivy import _n_frames

    task = ak.start(ak.n_frames(0))
    assert _n_frames._waiting_tasks == []
    assert task.finished


def test_n_frames_negative_number():
    import asynckivy as ak
    from asynckivy import _n_frames

    with pytest.raises(ValueError):
        ak.start(ak.n_frames(-2))
    assert _n_frames._waiting_tasks == []


def test_scoped_cancel():
    import asyncgui as ag
    import asynckivy as ak
    from kivy.clock import Clock
    TS = ag.TaskState

    async def async_fn(ctx):
        async with ag.open_cancel_scope() as scope:
            ctx['scope'] = scope
            await ak.one_frame()
            pytest.fail()
        await ag.sleep_forever()

    ctx = {}
    task = ag.start(async_fn(ctx))
    assert task.state is TS.STARTED
    ctx['scope'].cancel()
    assert task.state is TS.STARTED
    Clock.tick()
    assert task.state is TS.STARTED
    task._step()
    assert task.state is TS.FINISHED
