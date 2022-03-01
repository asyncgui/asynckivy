import pytest
p = pytest.mark.parametrize
p_order = p('order', ('lifo', 'fifo', 'priority'))
p_capacity = p('capacity', [1, 2, None, ])
p_capacity2 = p('capacity', [1, 2, 3, 4, None, ])


@pytest.fixture(autouse=True)
def autouse_kivy_clock(kivy_clock):
    pass


@p_order
def test_various_statistics(kivy_clock, order):
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=2, order=order)
    assert q.order == order
    assert len(q) == 0
    assert q.capacity == 2
    assert q.size == 0
    assert q.is_empty
    assert not q.is_full
    ak.start(q.put(1))
    assert q.size == 0
    assert q.is_empty
    assert not q.is_full
    kivy_clock.tick()
    assert q.size == 1
    assert not q.is_empty
    assert not q.is_full
    ak.start(q.put(2))
    assert q.size == 1
    assert not q.is_empty
    assert not q.is_full
    kivy_clock.tick()
    assert q.size == 2
    assert not q.is_empty
    assert q.is_full
    ak.start(q.get())
    assert q.size == 2
    assert not q.is_empty
    assert q.is_full
    kivy_clock.tick()
    assert q.size == 1
    assert not q.is_empty
    assert not q.is_full
    ak.start(q.get())
    assert q.size == 1
    assert not q.is_empty
    assert not q.is_full
    kivy_clock.tick()
    assert q.size == 0
    assert q.is_empty
    assert not q.is_full


@p_order
def test_various_statistics_nowait(order):
    from asynckivy.queue import Queue
    q = Queue(capacity=2, order=order)
    assert q.order == order
    assert len(q) == 0
    assert q.capacity == 2
    assert q.size == 0
    assert q.is_empty
    assert not q.is_full
    q.put_nowait(1)
    assert q.size == 1
    assert not q.is_empty
    assert not q.is_full
    q.put_nowait(2)
    assert q.size == 2
    assert not q.is_empty
    assert q.is_full
    q.get_nowait()
    assert q.size == 1
    assert not q.is_empty
    assert not q.is_full
    q.get_nowait()
    assert q.size == 0
    assert q.is_empty
    assert not q.is_full


@p_capacity
@p_order
def test_container_type(capacity, order):
    from asynckivy.queue import Queue
    q = Queue(capacity=capacity, order=order)
    if capacity != 1 and order == 'fifo':
        from collections import deque
        assert isinstance(q.container, deque)
    else:
        assert isinstance(q.container, list)


@p_capacity
def test_get_nowait_while_there_are_no_putters_and_no_items(capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=capacity)
    with pytest.raises(ak.WouldBlock):
        q.get_nowait()


@p_capacity
def test_get_nowait_while_there_is_a_putter_but_no_items(capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=capacity)
    ak.start(q.put('A'))
    with pytest.raises(ak.WouldBlock):
        q.get_nowait()


@p('capacity', [1, 2, ])
def test_put_nowait_while_there_are_no_getters_and_full_of_items(capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=capacity)
    for i in range(capacity):
        q._c_put(i)
    assert q.is_full
    with pytest.raises(ak.WouldBlock):
        q.put_nowait(99)


@p('capacity', [1, 2, ])
def test_put_nowait_while_there_is_a_getter_and_full_of_items(capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=capacity)
    for i in range(capacity):
        q._c_put(i)
    assert q.is_full
    ak.start(q.get())
    with pytest.raises(ak.WouldBlock):
        q.put_nowait(99)


def test_put_nowait_to_unbounded_queue_that_has_no_getters():
    from asynckivy.queue import Queue
    q = Queue(capacity=None)
    for i in range(10):
        q._c_put(i)
        assert not q.is_full
    q.put_nowait('A')


def test_put_nowait_to_unbounded_queue_that_has_a_getter():
    import asynckivy as ak
    from asynckivy.queue import Queue
    q = Queue(capacity=None)
    for i in range(10):
        q._c_put(i)
        assert not q.is_full
    ak.start(q.get())
    q.put_nowait('A')


@p('fullclose', [True, False, ])
@p_capacity2
def test_putter_triggers_close(kivy_clock, fullclose, capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer1(q):
        await q.put('A')
        q.fullclose() if fullclose else q.close()
    async def producer2(q):
        with pytest.raises(ak.ClosedResourceError):
            await q.put('B')
    async def consumer1(q):
        if fullclose:
            with pytest.raises(ak.ClosedResourceError):
                await q.get()
        else:
            assert await q.get() == 'A'
    async def consumer2(q):
        exc = ak.ClosedResourceError if fullclose else ak.EndOfResource
        with pytest.raises(exc):
            await q.get()

    q = Queue(capacity=capacity)
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
@p_capacity2
def test_getter_triggers_close(kivy_clock, fullclose, capacity):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer1(q):
        await q.put('A')
    async def producer2(q):
        if capacity is not None and capacity < 2:
            with pytest.raises(ak.ClosedResourceError):
                await q.put('B')
        else:
            await q.put('B')
    async def consumer1(q):
        assert await q.get() == 'A'
        q.fullclose() if fullclose else q.close()
    async def consumer2(q):
        if fullclose:
            with pytest.raises(ak.ClosedResourceError):
                await q.get()
        elif capacity is not None and capacity < 2:
            with pytest.raises(ak.EndOfResource):
                await q.get()
        else:
            assert await q.get() == 'B'

    q = Queue(capacity=capacity)
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


@p('capacity', [4, 5, None, ])
@p('order,input,expect', [('fifo', '0123', '0123'), ('lifo', '0123', '3210'), ('priority', '3102', '0123'), ])
def test_item_order__enough_capacity(kivy_clock, capacity, order, input, expect):
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q):
        for c in input:
            await q.put(int(c))
        q.close()

    async def consumer(q):
        return ''.join([str(i) async for i in q])

    q = Queue(capacity=capacity, order=order)
    p = ak.start(producer(q))
    c = ak.start(consumer(q))
    kivy_clock.tick()
    assert p.done
    assert c.result == expect


@p('order,input,expect', [('fifo', '0123', '0123'), ('lifo', '0123', '1032'), ('priority', '3102', '1302'), ])
def test_item_order_2capacity(kivy_clock, order, input, expect):
    '''NOTE: これは仕様というよりは現状の実装に対するtest'''
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q):
        for c in input:
            await q.put(int(c))
        q.close()

    async def consumer(q):
        return ''.join([str(i) async for i in q])

    q = Queue(capacity=2, order=order)
    p = ak.start(producer(q))
    c = ak.start(consumer(q))
    kivy_clock.tick()
    assert p.done
    assert c.result == expect


@p('order,input,expect', [('fifo', '0123', '0123'), ('lifo', '0123', '2103'), ('priority', '3102', '0132'), ])
def test_item_3capacity(kivy_clock, order, input, expect):
    '''NOTE: これは仕様というよりは現状の実装に対するtest'''
    import asynckivy as ak
    from asynckivy.queue import Queue

    async def producer(q):
        for c in input:
            await q.put(int(c))
        q.close()

    async def consumer(q):
        return ''.join([str(i) async for i in q])

    q = Queue(capacity=3, order=order)
    p = ak.start(producer(q))
    c = ak.start(consumer(q))
    kivy_clock.tick()
    assert p.done
    assert c.result == expect
