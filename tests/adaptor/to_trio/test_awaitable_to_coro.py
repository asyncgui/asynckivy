import pytest
pytest.importorskip('trio')


@pytest.mark.trio
async def test_return_value(nursery):
    import trio
    import asynckivy as ak
    from asynckivy.adaptor.to_trio import awaitable_to_coro

    async def ak_func(arg, *, kwarg):
        # ensure this function to be asynckivy-flavored
        e = ak.Event();e.set()
        await e.wait()

        assert arg == 'arg'
        assert kwarg == 'kwarg'
        return 'return_value'

    r = await awaitable_to_coro(ak_func('arg', kwarg='kwarg'))
    assert r == 'return_value'
