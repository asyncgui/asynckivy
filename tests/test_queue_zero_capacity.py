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


def test_container(q):
    assert q.container is None


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
    assert not p1.done
    assert not p2.done
    assert not c.done
    assert q.get_nowait() == 'A'
    assert p1.done
    assert p2.done
    assert c.done


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
    assert not p1.done
    assert not p2.done
    assert not c1.done
    assert not c2.done
    kivy_clock.tick()
    assert p1.done
    assert p2.done
    assert c1.done
    assert c2.done


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
    assert not p.done
    assert not c1.done
    assert not c2.done
    q.put_nowait('A')
    assert p.done
    assert c1.done
    assert c2.done


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
    assert not p1.done
    assert not p2.done
    assert not c1.done
    assert not c2.done
    kivy_clock.tick()
    assert p1.done
    assert p2.done
    assert c1.done
    assert c2.done


def test_cancel_putter(kivy_clock, q):
    import asynckivy as ak
    async def consumer(q):
        return ''.join([item async for item in q])
    p1 = ak.start(q.put('A'))
    p2 = ak.start(q.put('B'))
    c = ak.start(consumer(q))
    assert not p1.done
    assert not p2.done
    assert not c.done
    p1.cancel()
    kivy_clock.tick()
    assert p1.cancelled
    assert p2.done
    assert not c.done
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
    assert not p.done
    assert not c1.done
    assert not c2.done
    c1.cancel()
    kivy_clock.tick()
    assert p.done
    assert c1.cancelled
    assert c2.result == 'ABCD'


def test_wait_for_a_frame_before_get(kivy_clock, q):
    import asynckivy as ak
    p = ak.start(q.put('A'))
    kivy_clock.tick()
    assert not p.done
    c = ak.start(q.get())
    kivy_clock.tick()
    assert p.done
    assert c.result == 'A'


def test_wait_for_a_frame_before_put(kivy_clock, q):
    import asynckivy as ak
    c = ak.start(q.get())
    kivy_clock.tick()
    assert not c.done
    p = ak.start(q.put('A'))
    kivy_clock.tick()
    assert p.done
    assert c.result == 'A'
