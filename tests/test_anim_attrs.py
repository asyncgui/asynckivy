import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


def test_scalar(approx, kivy_runner):
    from types import SimpleNamespace
    import asynckivy as ak

    kr = kivy_runner
    obj = SimpleNamespace(num=0)
    task = ak.start(ak.anim_attrs(obj, num=100, duration=.4))

    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(25)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(50)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(75)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(100)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(100)
    assert task.finished


def test_list(approx, kivy_runner):
    from types import SimpleNamespace
    import asynckivy as ak

    kr = kivy_runner
    obj = SimpleNamespace(list=[0, 0])
    task = ak.start(ak.anim_attrs(obj, list=[100, 200], duration=.4))

    kr.advance_a_frame(dt=.1)
    assert obj.list == approx([25, 50])
    kr.advance_a_frame(dt=.1)
    assert obj.list == approx([50, 100])
    kr.advance_a_frame(dt=.1)
    assert obj.list == approx([75, 150])
    kr.advance_a_frame(dt=.1)
    assert obj.list == approx([100, 200])
    kr.advance_a_frame(dt=.1)
    assert obj.list == approx([100, 200])
    assert task.finished


def test_cancel(approx, kivy_runner):
    from types import SimpleNamespace
    import asynckivy as ak

    kr = kivy_runner
    obj = SimpleNamespace(num=0)
    task = ak.start(ak.anim_attrs(obj, num=100, duration=.4,))

    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(25)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(50)
    task.cancel()
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(50)


def test_low_fps(approx, kivy_runner):
    from types import SimpleNamespace
    import asynckivy as ak

    kr = kivy_runner
    obj = SimpleNamespace(num=0)
    task = ak.start(ak.anim_attrs(obj, num=100, duration=.4, step=.3))

    kr.advance_a_frame(dt=.1)
    assert obj.num == 0
    kr.advance_a_frame(dt=.1)
    assert obj.num == 0
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(75)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(75)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(75)
    kr.advance_a_frame(dt=.1)
    assert obj.num == approx(100)
    assert task.finished


def test_scoped_cancel(kivy_runner):
    from types import SimpleNamespace
    import asynckivy as ak
    TS = ak.TaskState
    kr = kivy_runner

    async def async_func():
        obj = SimpleNamespace(num=0)
        async with ak.move_on_when(e.wait()):
            await ak.anim_attrs(obj, num=100, duration=1)
            pytest.fail()
        await e.wait()

    e = ak.Event()
    task = ak.start(async_func())
    assert task.state is TS.STARTED
    kr.advance_a_frame(dt=.5)
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.STARTED
    kr.advance_a_frame(dt=1)
    assert task.state is TS.STARTED
    e.fire()
    assert task.state is TS.FINISHED
