import pytest


@pytest.mark.parametrize("n", range(3))
def test_non_negative_number_of_frames(kivy_runner, n):
    import asynckivy as ak
    kr = kivy_runner

    task = ak.start(ak.n_frames(n))
    for __ in range(n):
        assert not task.finished
        kr.advance_a_frame()
    assert task.finished


def test_cancel(kivy_runner):
    import asynckivy as ak
    kr = kivy_runner

    task = ak.start(ak.n_frames(2))
    assert not task.finished
    kr.advance_a_frame()
    assert not task.finished
    task.cancel()
    assert task.cancelled
    kr.advance_a_frame()
    kr.advance_a_frame()
    kr.advance_a_frame()


def test_negative_number_of_frames():
    import asynckivy as ak

    with pytest.raises(ValueError):
        ak.start(ak.n_frames(-2))


def test_scoped_cancel(kivy_runner):
    import asynckivy as ak
    kr = kivy_runner
    TS = ak.TaskState

    async def async_fn():
        async with ak.move_on_when(e.wait()):
            await ak.n_frames(1)
            pytest.fail()
        await e.wait()

    e = ak.Event()
    task = ak.start(async_fn())
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.STARTED
    kr.advance_a_frame()
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.FINISHED
