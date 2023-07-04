import pytest
p = pytest.mark.parametrize


@pytest.fixture()
def q(kivy_clock):  # Queue生成時にClockを使っているのでkivy_clockが要る
    from asynckivy.queue import Queue
    return Queue(capacity=0)


def test_size_and_len_and_capacity(q):
    import asynckivy as ak
    assert q.size == 0
    assert len(q) == 0
    assert q.capacity == 0
    ak.start(q.put('A'))
    assert q.size == 0
    assert len(q) == 0
    assert q.capacity == 0


def test_is_empty(q):
    import asynckivy as ak
    with pytest.raises(AttributeError):
        q.is_empty
    ak.start(q.put('A'))
    with pytest.raises(AttributeError):
        q.is_empty


def test_is_full(q):
    import asynckivy as ak
    with pytest.raises(AttributeError):
        q.is_full
    ak.start(q.put('A'))
    with pytest.raises(AttributeError):
        q.is_full


def test_order(q):
    assert q.order is None


def test_get_nowait_while_there_are_no_putters(q):
    import asynckivy as ak
    with pytest.raises(ak.WouldBlock):
        q.get_nowait()


def test_put_nowait_while_there_are_no_getters(q):
    import asynckivy as ak
    with pytest.raises(ak.WouldBlock):
        q.put_nowait('A')


@p('fullclose', [True, False, ])
def test_get_nowait_triggers_close(q, fullclose):
    import asynckivy as ak
    async def producer1(q):
        await q.put('A')
        q.fullclose() if fullclose else q.close()
    async def producer2(q):
        with pytest.raises(ak.ClosedResourceError):
            await q.put('B')
    async def consumer(q):
        with pytest.raises(ak.ClosedResourceError if fullclose else ak.EndOfResource):
            await q.get()
    p1 = ak.start(producer1(q))
    p2 = ak.start(producer2(q))
    c = ak.start(consumer(q))
    assert not p1.finished
    assert not p2.finished
    assert not c.finished
    assert q.get_nowait() == 'A'
    assert p1.finished
    assert p2.finished
    assert c.finished


@p('fullclose', [True, False, ])
def test_putter_triggers_close(kivy_clock, q, fullclose):
    import asynckivy as ak
    async def producer1(q):
        await q.put('A')
        q.fullclose() if fullclose else q.close()
    async def producer2(q):
        with pytest.raises(ak.ClosedResourceError):
            await q.put('B')
    async def consumer1(q):
        assert await q.get() == 'A'
    async def consumer2(q):
        with pytest.raises(ak.ClosedResourceError if fullclose else ak.EndOfResource):
            await q.get()
    p1 = ak.start(producer1(q))
    p2 = ak.start(producer2(q))
    c1 = ak.start(consumer1(q))
    c2 = ak.start(consumer2(q))
    assert not p1.finished
    assert not p2.finished
    assert not c1.finished
    assert not c2.finished
    kivy_clock.tick()
    assert p1.finished
    assert p2.finished
    assert c1.finished
    assert c2.finished


@p('fullclose', [True, False, ])
def test_put_nowait_triggers_close(q, fullclose):
    import asynckivy as ak
    async def producer(q):
        with pytest.raises(ak.ClosedResourceError):
            await q.put('B')
    async def consumer1(q):
        assert await q.get() == 'A'
        q.fullclose() if fullclose else q.close()
    async def consumer2(q):
        with pytest.raises(ak.ClosedResourceError if fullclose else ak.EndOfResource):
            await q.get()
    p = ak.start(producer(q))
    c1 = ak.start(consumer1(q))
    c2 = ak.start(consumer2(q))
    assert not p.finished
    assert not c1.finished
    assert not c2.finished
    q.put_nowait('A')
    assert p.finished
    assert c1.finished
    assert c2.finished


@p('fullclose', [True, False, ])
def test_getter_triggers_close(kivy_clock, q, fullclose):
    import asynckivy as ak
    async def producer1(q):
        await q.put('A')
    async def producer2(q):
        with pytest.raises(ak.ClosedResourceError):
            await q.put('B')
    async def consumer1(q):
        assert await q.get() == 'A'
        q.fullclose() if fullclose else q.close()
    async def consumer2(q):
        with pytest.raises(ak.ClosedResourceError if fullclose else ak.EndOfResource):
            await q.get()
    p1 = ak.start(producer1(q))
    p2 = ak.start(producer2(q))
    c1 = ak.start(consumer1(q))
    c2 = ak.start(consumer2(q))
    assert not p1.finished
    assert not p2.finished
    assert not c1.finished
    assert not c2.finished
    kivy_clock.tick()
    assert p1.finished
    assert p2.finished
    assert c1.finished
    assert c2.finished


def test_cancel_putter(kivy_clock, q):
    import asynckivy as ak
    async def consumer(q):
        return ''.join([item async for item in q])
    p1 = ak.start(q.put('A'))
    p2 = ak.start(q.put('B'))
    c = ak.start(consumer(q))
    assert not p1.finished
    assert not p2.finished
    assert not c.finished
    p1.cancel()
    kivy_clock.tick()
    assert p1.cancelled
    assert p2.finished
    assert not c.finished
    q.close()
    assert c.result == 'B'


def test_cancel_getter(kivy_clock, q):
    import asynckivy as ak
    async def producer(q):
        for i in 'ABCD':
            await q.put(i)
        q.close()
    async def consumer(q):
        return ''.join([item async for item in q])
    p = ak.start(producer(q))
    c1 = ak.start(consumer(q))
    c2 = ak.start(consumer(q))
    assert not p.finished
    assert not c1.finished
    assert not c2.finished
    c1.cancel()
    kivy_clock.tick()
    assert p.finished
    assert c1.cancelled
    assert c2.result == 'ABCD'


def test_wait_for_a_frame_before_get(kivy_clock, q):
    import asynckivy as ak
    p = ak.start(q.put('A'))
    kivy_clock.tick()
    assert not p.finished
    c = ak.start(q.get())
    kivy_clock.tick()
    assert p.finished
    assert c.result == 'A'


def test_wait_for_a_frame_before_put(kivy_clock, q):
    import asynckivy as ak
    c = ak.start(q.get())
    kivy_clock.tick()
    assert not c.finished
    p = ak.start(q.put('A'))
    kivy_clock.tick()
    assert p.finished
    assert c.result == 'A'


def test_scoped_cancel__get(kivy_clock, q):
    import asynckivy as ak

    async def async_fn(ctx):
        async with ak.open_cancel_scope() as scope:
            ctx['scope'] = scope
            ctx['state'] = 'A'
            await q.get()
            pytest.fail()
        ctx['state'] = 'B'
        await ak.sleep_forever()
        ctx['state'] = 'C'

    ctx = {}
    task = ak.start(async_fn(ctx))
    assert ctx['state'] == 'A'
    ctx['scope'].cancel()
    assert ctx['state'] == 'B'
    with pytest.raises(ak.WouldBlock):
        q.put_nowait('Hello')
    kivy_clock.tick()
    assert ctx['state'] == 'B'
    task._step()
    assert ctx['state'] == 'C'


def test_scoped_cancel__put(kivy_clock, q):
    import asynckivy as ak

    async def async_fn(ctx):
        async with ak.open_cancel_scope() as scope:
            ctx['scope'] = scope
            ctx['state'] = 'A'
            await q.put('Hello')
            pytest.fail()
        ctx['state'] = 'B'
        await ak.sleep_forever()
        ctx['state'] = 'C'

    ctx = {}
    task = ak.start(async_fn(ctx))
    assert ctx['state'] == 'A'
    ctx['scope'].cancel()
    assert ctx['state'] == 'B'
    with pytest.raises(ak.WouldBlock):
        q.get_nowait()
    kivy_clock.tick()
    assert ctx['state'] == 'B'
    task._step()
    assert ctx['state'] == 'C'
