import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


def test_scalar(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(num=0)
    task = ak.start(ak.anim_attrs(obj, num=100, duration=.4))

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
    assert task.finished


def test_list(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(list=[0, 0])
    task = ak.start(ak.anim_attrs(obj, list=[100, 200], duration=.4))

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
    assert task.finished


@pytest.mark.parametrize('output_seq_type', [list, tuple])
def test_output_seq_type_parameter(sleep_then_tick, output_seq_type):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(size=(0, 0), pos=[0, 0])
    task = ak.start(ak.anim_attrs(obj, size=[10, 10], pos=(10, 10), output_seq_type=output_seq_type))
    sleep_then_tick(.1)
    assert type(obj.size) is output_seq_type
    assert type(obj.pos) is output_seq_type
    task.cancel()


def test_cancel(approx, sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    obj = SimpleNamespace(num=0)
    task = ak.start(ak.anim_attrs(obj, num=100, duration=.4,))

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
    task = ak.start(ak.anim_attrs(obj, num=100, duration=.4, step=.3))

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
    assert task.finished


def test_scoped_cancel(sleep_then_tick):
    from types import SimpleNamespace
    import asynckivy as ak

    async def async_func(ctx):
        obj = SimpleNamespace(num=0)
        async with ak.open_cancel_scope() as scope:
            ctx['scope'] = scope
            ctx['state'] = 'A'
            await ak.anim_attrs(obj, num=100, duration=.1,)
            pytest.fail()
        ctx['state'] = 'B'
        await ak.sleep_forever()
        ctx['state'] = 'C'

    ctx = {}
    task = ak.start(async_func(ctx))
    assert ctx['state'] == 'A'
    ctx['scope'].cancel()
    assert ctx['state'] == 'B'
    sleep_then_tick(.2)
    assert ctx['state'] == 'B'
    task._step()
    assert ctx['state'] == 'C'
