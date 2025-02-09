import pytest


@pytest.mark.parametrize("n", range(3))
def test_non_negative_number_of_frames(kivy_clock, n):
    import asynckivy as ak

    task = ak.start(ak.n_frames(n))
    for __ in range(n):
        assert not task.finished
        kivy_clock.tick()
    assert task.finished


def test_cancel(kivy_clock):
    import asynckivy as ak

    task = ak.start(ak.n_frames(2))
    assert not task.finished
    kivy_clock.tick()
    assert not task.finished
    task.cancel()
    assert task.cancelled
    kivy_clock.tick()
    kivy_clock.tick()
    kivy_clock.tick()


def test_negative_number_of_frames():
    import asynckivy as ak

    with pytest.raises(ValueError):
        ak.start(ak.n_frames(-2))


def test_scoped_cancel(kivy_clock):
    import asynckivy as ak
    TS = ak.TaskState

    async def async_fn(ctx):
        async with ak.open_cancel_scope() as scope:
            ctx['scope'] = scope
            await ak.n_frames(1)
            pytest.fail()
        await ak.sleep_forever()

    ctx = {}
    task = ak.start(async_fn(ctx))
    assert task.state is TS.STARTED
    ctx['scope'].cancel()
    assert task.state is TS.STARTED
    kivy_clock.tick()
    assert task.state is TS.STARTED
    task._step()
    assert task.state is TS.FINISHED
