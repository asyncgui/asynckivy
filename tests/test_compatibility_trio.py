import pytest
pytest.importorskip('trio')


@pytest.fixture(scope='module')
def ed_cls():
    from kivy.event import EventDispatcher
    class ConcreteEventDispatcher(EventDispatcher):
        __events__ = ('on_test', )
        def on_test(self, *args, **kwargs):
            pass
    return ConcreteEventDispatcher


@pytest.fixture()
def ed(ed_cls):
    return ed_cls()


@pytest.mark.trio
async def test_normal_exit(nursery, ed):
    from inspect import getcoroutinestate, CORO_SUSPENDED, CORO_CLOSED
    import trio
    import asynckivy as ak
    from asynckivy.compatibility.trio import run_coro_under_trio
    
    async def ak_func():
        await ak.event(ed, 'on_test')
    ak_coro = ak_func()
    async def trio_func(*, task_status=trio.TASK_STATUS_IGNORED):
        await run_coro_under_trio(ak_coro, task_status=task_status)
        nonlocal done; done = True

    done = False
    await nursery.start(trio_func)
    assert getcoroutinestate(ak_coro) == CORO_SUSPENDED
    assert not done
    ed.dispatch('on_test')
    assert getcoroutinestate(ak_coro) == CORO_CLOSED
    await trio.sleep(.01)
    assert done


@pytest.mark.trio
async def test_normal_exit2(nursery, ed):
    '''nursery.start_soon() instead of nursery.start()'''
    from inspect import (
        getcoroutinestate, CORO_CREATED, CORO_SUSPENDED, CORO_CLOSED,
    )
    import trio
    import asynckivy as ak
    from asynckivy.compatibility.trio import run_coro_under_trio
    
    async def ak_func():
        await ak.event(ed, 'on_test')
    ak_coro = ak_func()
    async def trio_func():
        await run_coro_under_trio(ak_coro)
        nonlocal done; done = True

    done = False
    nursery.start_soon(trio_func)
    assert getcoroutinestate(ak_coro) == CORO_CREATED
    assert not done
    await trio.sleep(.01)
    assert getcoroutinestate(ak_coro) == CORO_SUSPENDED
    assert not done
    ed.dispatch('on_test')
    assert getcoroutinestate(ak_coro) == CORO_CLOSED
    await trio.sleep(.01)
    assert done


@pytest.mark.xfail(strict=True)
@pytest.mark.trio
async def test_exceptions_are_properly_propagated(nursery, ed):
    import trio
    import asynckivy as ak
    from asynckivy.compatibility.trio import run_coro_under_trio
    
    class MyException(Exception):
        pass
    async def ak_func():
        await ak.event(ed, 'on_test')
        raise MyException()
    async def trio_func(*, task_status=trio.TASK_STATUS_IGNORED):
        try:
            await run_coro_under_trio(ak_func(), task_status=task_status)
        except MyException:
            nonlocal done; done = True

    done = False
    await nursery.start(trio_func)
    ed.dispatch('on_test')
    await trio.sleep(.01)
    assert done


@pytest.mark.trio
async def test_cancel_from_trio(nursery):
    import trio
    import asynckivy as ak
    from asynckivy.compatibility.trio import run_coro_under_trio
    
    async def ak_func():
        try:
            await ak.sleep_forever()
        except GeneratorExit:
            nonlocal done; done = True
            raise
    ak_coro = ak_func()
    async def trio_func(*, task_status=trio.TASK_STATUS_IGNORED):
        with trio.CancelScope() as scope:
            task_status.started(scope)
            await run_coro_under_trio(ak_coro)

    done = False
    scope = await nursery.start(trio_func)
    assert not done
    scope.cancel()
    await trio.sleep(.01)
    assert done
