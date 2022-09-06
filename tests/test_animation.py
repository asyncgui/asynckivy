import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


def test_scalar(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(num=0)
    task = ak.start(ak.animate(obj, num=100, duration=.4))

    sleep_then_tick(.1)
    assert obj.num == approx(25)
    sleep_then_tick(.1)
    assert obj.num == approx(50)
    sleep_then_tick(.1)
    assert obj.num == approx(75)
    sleep_then_tick(.1)
    assert obj.num == approx(100)
    sleep_then_tick(.1)
    assert obj.num == approx(100)
    assert task.done


def test_list(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(list=[0, 0])
    task = ak.start(ak.animate(obj, list=[100, 200], duration=.4))

    sleep_then_tick(.1)
    assert obj.list == approx([25, 50])
    sleep_then_tick(.1)
    assert obj.list == approx([50, 100])
    sleep_then_tick(.1)
    assert obj.list == approx([75, 150])
    sleep_then_tick(.1)
    assert obj.list == approx([100, 200])
    sleep_then_tick(.1)
    assert obj.list == approx([100, 200])
    assert task.done


def test_dict(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(dict={'key': 0., })
    task = ak.start(ak.animate(obj, dict={'key': 100}, duration=.4))

    sleep_then_tick(.1)
    assert obj.dict == approx({'key': 25})
    sleep_then_tick(.1)
    assert obj.dict == approx({'key': 50})
    sleep_then_tick(.1)
    assert obj.dict == approx({'key': 75})
    sleep_then_tick(.1)
    assert obj.dict == approx({'key': 100})
    sleep_then_tick(.1)
    assert obj.dict == approx({'key': 100})
    assert task.done


def test_cancel(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(num=0)
    task = ak.start(ak.animate(obj, num=100, duration=.4,))

    sleep_then_tick(.1)
    assert obj.num == approx(25)
    sleep_then_tick(.1)
    assert obj.num == approx(50)
    task.cancel()
    sleep_then_tick(.1)
    assert obj.num == approx(50)


def test_low_fps(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(num=0)
    task = ak.start(ak.animate(obj, num=100, duration=.4, step=.3))

    sleep_then_tick(.1)
    assert obj.num == 0
    sleep_then_tick(.1)
    assert obj.num == 0
    sleep_then_tick(.1)
    assert obj.num == approx(75)
    sleep_then_tick(.1)
    assert obj.num == approx(75)
    sleep_then_tick(.1)
    assert obj.num == approx(75)
    sleep_then_tick(.1)
    assert obj.num == approx(100)
    assert task.done
