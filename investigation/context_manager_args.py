class cm_1:
    __slots__ = ('_disp', '_name', '_filter', '_stop', )

    def __init__(self, event_dispatcher, event_name, *, filter=None, stop_dispatching=False):
        self._disp = event_dispatcher
        self._name = event_name
        self._filter = filter
        self._stop = stop_dispatching

    def __enter__(self):
        event_dispatcher = self._disp
        event_name = self._name
        filter = self._filter
        stop_dispatching = self._stop

    def __exit__(self, *args):
        event_dispatcher = self._disp
        event_name = self._name
        filter = self._filter
        stop_dispatching = self._stop


class cm_2:
    __slots__ = ('_args', )

    def __init__(self, event_dispatcher, event_name, *, filter=None, stop_dispatching=False):
        self._args = (event_dispatcher, event_name, filter, stop_dispatching)

    def __enter__(self):
        event_dispatcher, event_name, filter, stop_dispatching = self._args

    def __exit__(self, *args):
        event_dispatcher, event_name, filter, stop_dispatching = self._args


from functools import partial
from timeit import timeit

def test(cm_func):
    with cm_func(None, None, filter=None, stop_dispatching=None):
        pass


cm_1_result = timeit(partial(test, cm_1))
cm_2_result = timeit(partial(test, cm_2))
print(f"cm_1 time: {cm_1_result:.6f} seconds")
print(f"cm_2 time: {cm_2_result:.6f} seconds")
