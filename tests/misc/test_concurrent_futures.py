import pytest
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

executor_classes = (ThreadPoolExecutor, ProcessPoolExecutor, )
try:
    from concurrent.futures import InterpreterPoolExecutor
except ImportError:  # Introduced in Python 3.14
    pass
else:
    executor_classes += (InterpreterPoolExecutor, )
executor_cls = pytest.mark.parametrize("executor_cls", executor_classes)


@executor_cls
def test_cancel_before_start_executing_1(executor_cls):
    with executor_cls(max_workers=1) as executor:
        executor.submit(time.sleep, 2)
        time.sleep(.5)
        fut = executor.submit(time.sleep, 1)
        assert fut.cancel()


@executor_cls
def test_cancel_before_start_executing_2(executor_cls):
    with executor_cls(max_workers=1) as executor:
        executor.submit(time.sleep, 2)
        time.sleep(.5)
        fut = executor.submit(time.sleep, 1)
        time.sleep(.5)
        assert fut.cancel() is (executor_cls is not ProcessPoolExecutor)
