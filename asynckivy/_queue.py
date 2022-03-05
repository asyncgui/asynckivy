'''
Notes for maintainers
---------------------

ZeroCapacityQueue(以後はZQと略す)とNormalQueue(以後はNQと略す)は容量以外にも以下の違いがある。

- ZQは get_nowait() 時にputterを見に行くのに対しNQは見に行かない。なのでNQはputterがあったとしてもキューが空の時はWouldBlockを起こす。
- put_nowait() も同じで、NQはgetterを見に行かないのでgetterがあったとしてもキューが満タンの時はWouldBlockを起こす。
- ZQではitemの中継はputterとgetterの両方を同時に取り出てから行うため、putterを進めた時にキューを閉じられたとしてもgetterには影響しない。
  対してNQでは同時に取り出さないため、putterを進めた時にキューが閉じられればgetterはその影響をうける。

これらの違いは無くそうと思えば無くせるかもしれないが実装がかなり複雑になるので諦めた。
'''

__all__ = ('ZeroCapacityQueue', 'NormalQueue', )
from typing import Tuple, Any
import types
from functools import partial
from collections import deque
from kivy.clock import Clock
from asynckivy import sleep_forever, TaskState, Task, get_current_task
from asynckivy.exceptions import WouldBlock, ClosedResourceError, EndOfResource


Item = Any  # type-hint for queue item


class ZeroCapacityQueue:
    '''Queue, optimized for zero capacity'''

    def __init__(self):
        self._allows_to_put = True
        self._allows_to_get = True
        self._putters = deque()  # queue of tuple(task, item) s
        self._getters = deque()  # queue of task._step_coro s
        self._trigger_consume = Clock.create_trigger(self._consume)

    def __len__(self):
        return 0
    size = property(__len__)

    @property
    def capacity(self) -> int:
        return 0

    @property
    def is_empty(self):
        raise AttributeError("The meaning of 'empty' is ambiguous for a zero capacity queue.")

    @property
    def is_full(self):
        raise AttributeError("The meaning of 'full' is ambiguous for a zero capacity queue.")

    @property
    def order(self):
        return None

    @types.coroutine
    def get(self):
        if not self._allows_to_get:
            raise ClosedResourceError
        if not self._allows_to_put:
            raise EndOfResource
        self._trigger_consume()
        return (yield self._getters.append)[0][0]

    def get_nowait(self):
        if not self._allows_to_get:
            raise ClosedResourceError
        if not self._allows_to_put:
            raise EndOfResource
        putter, item = self._pop_putter()
        if putter is None:
            raise WouldBlock
        putter._step_coro()
        return item

    async def put(self, item):
        if not self._allows_to_put:
            raise ClosedResourceError
        self._trigger_consume()
        self._putters.append((await get_current_task(), item, ))
        await sleep_forever()

    def put_nowait(self, item):
        if not self._allows_to_put:
            raise ClosedResourceError
        getter = self._pop_getter()
        if getter is None:
            raise WouldBlock
        getter._step_coro(item)

    def close(self):
        self._allows_to_put = False

        # LOAD_FAST
        pop_putter = self._pop_putter
        pop_getter = self._pop_getter
        CRE = ClosedResourceError
        EOR = EndOfResource

        # TODO: refactor after python3.7 ends
        while True:
            putter, __ = pop_putter()
            if putter is None:
                break
            putter._throw_exc(CRE)
        while True:
            getter = pop_getter()
            if getter is None:
                break
            getter._throw_exc(EOR)

    def fullclose(self):
        self._allows_to_put = False
        self._allows_to_get = False

        # LOAD_FAST
        CRE = ClosedResourceError
        pop_putter = self._pop_putter
        pop_getter = self._pop_getter

        # TODO: refactor after python3.7 ends
        while True:
            task, __ = pop_putter()
            if task is None:
                break
            task._throw_exc(CRE)
        while True:
            task = pop_getter()
            if task is None:
                break
            task._throw_exc(CRE)

    async def __aiter__(self):
        try:
            while True:
                yield await self.get()
        except EndOfResource:
            pass

    def _consume(self, __):
        # LOAD_FAST
        pop_putter = self._pop_putter
        pop_getter = self._pop_getter

        while True:
            getter = pop_getter()
            if getter is None:
                break
            putter, item = pop_putter()
            if putter is None:
                self._getters.appendleft(getter._step_coro)
                break
            putter._step_coro()
            getter._step_coro(item)
        self._trigger_consume.cancel()

    def _pop_getter(self, *, _STARTED=TaskState.STARTED) -> Task:
        '''Take out a next getter. Return None if no one is available.'''
        getters = self._getters
        while getters:
            task = getters.popleft().__self__
            if task.state is _STARTED:
                return task

    def _pop_putter(self, *, _STARTED=TaskState.STARTED) -> Tuple[Task, Item]:
        '''Take out a next putter and its item. Return (None, None) if no one is available.'''
        putters = self._putters
        while putters:
            task, item = putters.popleft()
            if task.state is _STARTED:
                return (task, item, )
        return (None, None, )


class NormalQueue:
    def __init__(self, *, capacity, order):
        self._allows_to_put = True
        self._allows_to_get = True
        self._putters = deque()  # queue of tuple(task, item) s
        self._getters = deque()  # queue of task._step_coro s
        self._trigger_consume = Clock.create_trigger(self._consume)
        self._init_container(capacity, order)
        self._capacity = capacity
        self._order = order

    def _init_container(self, capacity, order):
        # If the capacity is 1, there is no point of re-ordering items.
        # Therefore, does not use heapq for a performance reason.
        if capacity == 1 or order == 'lifo':
            c = []
            c_get = c.pop
            c_put = c.append
        elif order == 'fifo':
            c = deque(maxlen=capacity)
            c_get = c.popleft
            c_put = c.append
        elif order == 'small-first':
            import heapq
            c = []
            c_get = partial(heapq.heappop, c)
            c_put = partial(heapq.heappush, c)
        else:
            raise ValueError("'order' must be one of 'lifo', 'fifo' or 'small-first'.")
        self._c = c
        self._c_get = c_get
        self._c_put = c_put

    def __len__(self):
        return len(self._c)
    size = property(__len__)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def is_empty(self):
        return not self._c

    @property
    def is_full(self):
        return len(self._c) == self._capacity

    @property
    def order(self):
        return self._order

    @types.coroutine
    def get(self):
        if not self._allows_to_get:
            raise ClosedResourceError
        if (not self._allows_to_put) and self.is_empty:
            raise EndOfResource
        self._trigger_consume()
        return (yield self._getters.append)[0][0]

    def get_nowait(self):
        if not self._allows_to_get:
            raise ClosedResourceError
        if self.is_empty:
            if self._allows_to_put:
                raise WouldBlock
            raise EndOfResource
        self._trigger_consume()
        return self._c_get()

    put = ZeroCapacityQueue.put

    def put_nowait(self, item):
        if not self._allows_to_put:
            raise ClosedResourceError
        if self.is_full:
            raise WouldBlock
        self._c_put(item)
        self._trigger_consume()

    def close(self):
        self._allows_to_put = False

        # LOAD_FAST
        pop_putter = self._pop_putter
        pop_getter = self._pop_getter
        CRE = ClosedResourceError
        EOR = EndOfResource

        # TODO: refactor after python3.7 ends
        while True:
            putter, __ = pop_putter()
            if putter is None:
                break
            putter._throw_exc(CRE)
        if not self.is_empty:
            return
        while True:
            getter = pop_getter()
            if getter is None:
                break
            getter._throw_exc(EOR)

    def fullclose(self):
        self._c.clear()
        ZeroCapacityQueue.fullclose(self)

    __aiter__ = ZeroCapacityQueue.__aiter__

    def _consume(self, __):
        # LOAD_FAST
        getters = self._getters
        putters = self._putters
        pop_putter = self._pop_putter
        pop_getter = self._pop_getter
        c_put = self._c_put
        c_get = self._c_get

        while True:
            while not self.is_full:
                putter, item = pop_putter()
                if putter is None:
                    break
                c_put(item)
                putter._step_coro()
            if (not getters) or self.is_empty:
                break
            while not self.is_empty:
                getter = pop_getter()
                if getter is None:
                    break
                getter._step_coro(c_get())
            else:
                if not self._allows_to_put:
                    EOR = EndOfResource  # LOAD_FAST
                    while True:  # TODO: refactor after Python3.7 ends
                        getter = pop_getter()
                        if getter is None:
                            break
                        getter._throw_exc(EOR)
            if (not putters) or self.is_full:
                break
        self._trigger_consume.cancel()

    _pop_getter = ZeroCapacityQueue._pop_getter
    _pop_putter = ZeroCapacityQueue._pop_putter
