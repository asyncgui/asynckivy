import pytest
pytest.importorskip('trio')


@pytest.mark.trio
async def test_nursery_start(nursery):
    from inspect import getcoroutinestate, CORO_SUSPENDED, CORO_CLOSED
    import trio
    import asynckivy as ak
    from asynckivy.adaptor.to_trio import callable_to_asyncfn

    ak_event = ak.Event()
    trio_event = trio.Event()
    async def ak_func():
        await ak_event.wait()
        trio_event.set()

    with trio.fail_after(1):
        ak_wrapper_coro = await nursery.start(callable_to_asyncfn(ak_func))
        assert getcoroutinestate(ak_wrapper_coro) == CORO_SUSPENDED
        ak_event.set()
        assert getcoroutinestate(ak_wrapper_coro) == CORO_CLOSED
        await trio_event.wait()


@pytest.mark.trio
async def test_nursery_start_soon(nursery):
    import trio
    import asynckivy as ak
    from asynckivy.adaptor.to_trio import callable_to_asyncfn

    ak_event = ak.Event()
    trio_event1 = trio.Event()
    trio_event2 = trio.Event()
    async def ak_func():
        trio_event1.set()
        await ak_event.wait()
        trio_event2.set()

    with trio.fail_after(1):
        nursery.start_soon(callable_to_asyncfn(ak_func))
        await trio_event1.wait()
        ak_event.set()
        await trio_event2.wait()


@pytest.mark.trio
async def test_cancel_from_trio(nursery):
    import trio
    import asynckivy as ak
    from asynckivy.adaptor.to_trio import callable_to_asyncfn

    ak_event = ak.Event()
    trio_event = trio.Event()
    cancel_scope = None
    async def trio_func(*, task_status):
        nonlocal cancel_scope; cancel_scope = trio.CancelScope()
        with cancel_scope:
            await callable_to_asyncfn(ak_event.wait)(task_status=task_status)
        trio_event.set()

    with trio.fail_after(1):
        await nursery.start(trio_func)
        cancel_scope.cancel()
        await trio_event.wait()
        assert not ak_event.is_set()


@pytest.mark.trio
async def test_cancel_from_asynckivy(nursery):
    import trio
    import asynckivy as ak
    from asynckivy.adaptor.to_trio import callable_to_asyncfn

    ak_event = ak.Event()
    trio_event = trio.Event()
    async def trio_func(*, task_status):
        with pytest.raises(ak.exceptions.CancelledError):
            await callable_to_asyncfn(ak_event.wait)(task_status=task_status)
        trio_event.set()

    with trio.fail_after(1):
        ak_wrapper_coro = await nursery.start(trio_func)
        ak_wrapper_coro.close()
        await trio_event.wait()
        assert not ak_event.is_set()


@pytest.mark.trio
async def test_exception_propagation(nursery):
    import trio
    import asynckivy as ak
    from asynckivy.adaptor.to_trio import callable_to_asyncfn

    ak_event = ak.Event()
    trio_event = trio.Event()
    async def ak_func():
        await ak_event.wait()
        raise ZeroDivisionError
    async def trio_func(*, task_status):
        with pytest.raises(ZeroDivisionError):
            await callable_to_asyncfn(ak_func)(task_status=task_status)
        trio_event.set()

    with trio.fail_after(1):
        await nursery.start(trio_func)
        ak_event.set()
        await trio_event.wait()
