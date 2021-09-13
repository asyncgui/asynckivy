import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=2)


def test_complete_iteration(approx, ready_to_sleep):
    import asynckivy as ak

    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100, step=.3)]
        assert l == approx([0, 30, 60, 90, 100])

    sleep = ready_to_sleep()
    task = ak.start(job())
    for __ in range(130):
        sleep(.01)
    assert task.done


def test_break_during_iteration(approx, ready_to_sleep):
    import asynckivy as ak

    async def job():
        l = []
        async for v in ak.interpolate(start=0, end=100, step=.3):
            l.append(v)
            if v > 50:
                break
        assert l == approx([0, 30, 60, ])
        await ak.sleep_forever()

    sleep = ready_to_sleep()
    task = ak.start(job())
    for __ in range(130):
        sleep(.01)
    assert not task.done
    with pytest.raises(StopIteration):
        task.root_coro.send(None)
    assert task.done


def test_zero_duration(approx):
    import asynckivy as ak

    async def job():
        l = [v async for v in ak.interpolate(start=0, end=100, step=.3, d=0)]
        assert l == approx([0, 100])

    task = ak.start(job())
    assert task.done
