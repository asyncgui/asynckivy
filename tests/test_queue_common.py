import pytest
p = pytest.mark.parametrize
p_capacity = p('capacity', [0, 1, 2, None, ])
p_capacity2 = p('capacity', [0, 1, 2, 3, 4, None, ])


@pytest.fixture(autouse=True)
def autouse_kivy_clock(kivy_clock):
    pass


@p('capacity', (-1., 0., 1., "", "str", tuple(), [], ))
def test_invalid_capacity_type(capacity):
    from asynckivy.queue import Queue
    with pytest.raises(TypeError):
        Queue(capacity=capacity)


@p('capacity', (-1, ))
def test_invalid_capacity_value(capacity):
    from asynckivy.queue import Queue
    with pytest.raises(ValueError):
        Queue(capacity=capacity)


@p_capacity
@p('order', ['fifo', 'lifo', 'small-first', ])
def test_instance_type(capacity, order):
    from asynckivy.queue import Queue
    from asynckivy._queue import ZeroCapacityQueue, NormalQueue
    q = Queue(capacity=capacity, order=order)
    if capacity == 0:
        assert isinstance(q, ZeroCapacityQueue)
    else:
        assert isinstance(q, NormalQueue)


@p_capacity
@p('fullclose', [True, False, ])
@p('nowait', [True, False, ])
def test_put_to_closed_queue(capacity, fullclose, nowait):
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=capacity)
    q.fullclose() if fullclose else q.close()
    with pytest.raises(ak.ClosedResourceError):
        q.put_nowait('Z') if nowait else ak.start(q.put('Z'))


@p_capacity
@p('fullclose', [True, False, ])
@p('nowait', [True, False, ])
def test_get_to_closed_queue(capacity, fullclose, nowait):
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=capacity)
    if fullclose:
        q.fullclose()
        exc = ak.ClosedResourceError
    else:
        q.close()
        exc = ak.EndOfResource
    with pytest.raises(exc):
        q.get_nowait() if nowait else ak.start(q.get())


@p_capacity2
def test_async_for(kivy_clock, capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q, items):
        for i in items:
            await q.put(i)

    async def consumer(q):
        return ''.join([item async for item in q])

    q = Queue(capacity=capacity)
    p = ak.start(producer(q, 'ABC'))
    c = ak.start(consumer(q))
    assert not p.finished
    assert not c.finished
    kivy_clock.tick()
    assert p.finished
    assert not c.finished
    q.close()
    assert c.result == 'ABC'


@p_capacity2
def test_one_producer_and_two_consumers(kivy_clock, capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q):
        for c in 'A1B2C3':
            await q.put(c)
        q.close()

    async def consumer(q):
        return ''.join([item async for item in q])

    q = Queue(capacity=capacity)
    p = ak.start(producer(q))
    c1 = ak.start(consumer(q))
    c2 = ak.start(consumer(q))
    assert not p.finished
    assert not c1.finished
    assert not c2.finished
    kivy_clock.tick()
    assert p.finished
    assert c1.result == 'ABC'
    assert c2.result == '123'


@p_capacity2
def test_two_producers_and_one_consumer(kivy_clock, capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q, items):
        for i in items:
            await q.put(i)

    async def consumer(q):
        return ''.join([item async for item in q])

    q = Queue(capacity=capacity)
    p1 = ak.start(producer(q, 'ABC'))
    p2 = ak.start(producer(q, '123'))
    c = ak.start(consumer(q))
    assert not p1.finished
    assert not p2.finished
    assert not c.finished
    kivy_clock.tick()
    assert p1.finished
    assert p2.finished
    assert not c.finished
    q.close()
    assert c.result == 'A1B2C3'


@p_capacity2
def test_two_producers_and_two_consumers(kivy_clock, capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q, items):
        for i in items:
            await q.put(i)

    async def consumer(q):
        return ''.join([item async for item in q])

    q = Queue(capacity=capacity)
    p1 = ak.start(producer(q, 'ABC'))
    p2 = ak.start(producer(q, '123'))
    c1 = ak.start(consumer(q))
    c2 = ak.start(consumer(q))
    assert not p1.finished
    assert not p2.finished
    assert not c1.finished
    assert not c2.finished
    kivy_clock.tick()
    assert p1.finished
    assert p2.finished
    assert not c1.finished
    assert not c2.finished
    q.close()
    assert c1.result == 'ABC'
    assert c2.result == '123'


@p('n_producers', range(3))
@p('n_consumers', range(3))
@p('fullclose', [True, False, ])
@p_capacity2
def test_close_a_queue_while_it_holding_putters_and_getters(n_producers, n_consumers, fullclose, capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q):
        with pytest.raises(ak.ClosedResourceError):
            await q.put(None)
    async def consumer(q):
        with pytest.raises(ak.ClosedResourceError if fullclose else ak.EndOfResource):
            await q.get()

    q = Queue(capacity=capacity)
    producers = [ak.start(producer(q)) for __ in range(n_producers)]
    consumers = [ak.start(consumer(q)) for __ in range(n_consumers)]
    for p in producers:
        assert not p.finished
    for c in consumers:
        assert not c.finished
    q.fullclose() if fullclose else q.close()
    for p in producers:
        assert p.finished
    for c in consumers:
        assert c.finished
