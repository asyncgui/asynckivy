__all__ = ('Queue', )
from typing import Union


class Queue:
    @property
    def size(self) -> int:
        '''Number of items in the queue. This equals to ``len(queue)``. '''

    @property
    def capacity(self) -> Union[int, None]:
        '''Number of items allowed in the queue. None if unbounded.'''

    @property
    def is_empty(self) -> bool:
        '''Whether the queue is empty. Raise AttributeError if the capacity of the queue is zero.'''

    @property
    def is_full(self) -> bool:
        '''Whether the queue is full. Raise AttributeError if the capacity of the queue is zero.'''

    @property
    def order(self) -> Union[str, None]:
        ''' 'fifo', 'lifo' or 'small-first'. None if the capacity of the queue is zero. '''

    async def get(self):
        '''Take out an item from the queue. If one is not available, wait until it is.
        If the queue is empty, and is partially closed, raise EndOfResource.
        If the queue is fully closed, raise ClosedResourceError.
        '''

    def get_nowait(self):
        '''Take out an item from the queue if one is immediately available, else raise WouldBlock.
        Everything else is the same as ``get``.
        '''

    async def put(self, item):
        '''Put an item into the queue. If no free slots are available, wait until one is available.
        If the queue is partially or fully closed, raise ClosedResourceError.
        '''

    def put_nowait(self, item):
        '''Put an item into the queue if a free slot is immediately available, else raise WouldBlock.
        Everything else is the same as ``put``.
        '''

    def close(self):
        '''Partially close the queue. No further putting opeations are allowed. '''

    def fullclose(self):
        '''Fully close the queue. No further putting/getting operations are allowed. All items in the queue are
        discarded.
        '''

    def __aiter__(self):
        '''Return an async iterator that repeatedly ``get`` an item from the queue until it raises EndOfResource.'''

    def __init__(self, *, capacity: Union[int, None]=0, order='fifo'):
        '''
        :Parameters:
            `capacity`: int, defaults to 0
                If this is None, the queue will have infinite capacity.
            `order`: str, defaults to 'fifo'
                The order of the queue items. One of 'fifo', 'lifo' or 'small-first'.
        '''
        # 単に False だと私が使っているeditor(Visual Studio Code)の色付けが崩れてしまう為 bool(False)
        assert bool(False), "This is an abstract class"

    def __new__(cls, *, capacity: Union[int, None]=0, order='fifo'):
        from . import _queue
        if capacity is None:
            pass
        elif isinstance(capacity, int):
            if capacity == 0:
                return _queue.ZeroCapacityQueue()
            elif capacity < 0:
                raise ValueError(f"If 'capacity' is an integer, it must be zero or greater. (was {capacity})")
        else:
            raise TypeError(f"'capacity' must be None or an integer. (was {type(capacity)})")
        return _queue.NormalQueue(capacity=capacity, order=order)
