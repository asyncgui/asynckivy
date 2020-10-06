import pytest
pytest.importorskip('trio')


@pytest.mark.trio
async def test_arguments_and_return_value(nursery):
    import trio
    import asynckivy as ak
    from asynckivy.adaptor.to_trio import callable_to_asyncfn

    async def ak_func(arg, *, kwarg):
        # ensure this function to be asynckivy-flavored
        e = ak.Event();e.set()
        await e.wait()

        assert arg == 'arg'
        assert kwarg == 'kwarg'
        return 'return_value'

    await callable_to_asyncfn(ak_func)('arg', kwarg='kwarg') == 'return_value'


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

    state = 'A'
    ak_event = ak.Event()
    trio_event = trio.Event()
    async def ak_func():
        nonlocal state
        assert state == 'B'
        state = 'C'
        trio_event.set()
        await ak_event.wait()
        assert state == 'D'

    with trio.fail_after(1):
        nursery.start_soon(callable_to_asyncfn(ak_func))
        assert state == 'A'
        state = 'B'
        await trio_event.wait()
        assert state == 'C'
        state = 'D'
        ak_event.set()


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

    trio_event = trio.Event()
    async def ak_func():
        # ensure this function to be asynckivy-flavored
        e = ak.Event();e.set()
        await e.wait()

        raise ZeroDivisionError
    async def trio_func(*, task_status):
        with pytest.raises(ZeroDivisionError):
            await callable_to_asyncfn(ak_func)(task_status=task_status)
        trio_event.set()

    with trio.fail_after(1):
        await nursery.start(trio_func)
        await trio_event.wait()
