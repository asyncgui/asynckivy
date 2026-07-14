import pytest
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import threading

executor_classes = (ThreadPoolExecutor, ProcessPoolExecutor, )
try:
    from concurrent.futures import InterpreterPoolExecutor
except ImportError:  # Introduced in Python 3.14
    pass
else:
    executor_classes += (InterpreterPoolExecutor, )
executor_cls = pytest.mark.parametrize("executor_cls", executor_classes)


def fail_immediately():
    1 / 0


def fail_eventually():
    import time; time.sleep(1)
    1 / 0


def finish_immediately():
    return "ROTK9"


def finish_eventually():
    import time; time.sleep(1)
    return "ROTK9"


@executor_cls
def test_caller_coroutine_resumes_in_the_same_thread_where_it_paused(kivy_runner, executor_cls):
    import asynckivy as ak

    async def job(executor):
        before = threading.get_ident()
        await ak.run_in_executor(executor, finish_immediately)
        after = threading.get_ident()
        return before == after

    with executor_cls() as executor:
        task = ak.start(job(executor))
        for _ in range(4):
            time.sleep(.5)
            kivy_runner.advance_a_frame()
            if task.finished:
                break
        else:
            pytest.fail("Task is taking too much time to finish")
        assert task.result


@executor_cls
def test_finish_immediately(kivy_runner, executor_cls):
    import asynckivy as ak

    with executor_cls() as executor:
        task = ak.start(ak.run_in_executor(executor, finish_immediately))
        for _ in range(4):
            time.sleep(.5)
            kivy_runner.advance_a_frame()
            if task.finished:
                break
        else:
            pytest.fail("Task is taking too much time to finish")
        assert task.result == "ROTK9"


@executor_cls
def test_fail_immediately(kivy_runner, executor_cls):
    import asynckivy as ak

    async def job(executor):
        with pytest.raises(ZeroDivisionError):
            await ak.run_in_executor(executor, fail_immediately)

    with executor_cls() as executor:
        task = ak.start(job(executor))
        for _ in range(4):
            time.sleep(.5)
            kivy_runner.advance_a_frame()
            if task.finished:
                break
        else:
            pytest.fail("Task is taking too much time to finish")


@executor_cls
def test_finish_eventually(kivy_runner, executor_cls):
    import asynckivy as ak

    with executor_cls() as executor:
        task = ak.start(ak.run_in_executor(executor, finish_eventually))
        for _ in range(6):
            time.sleep(.5)
            kivy_runner.advance_a_frame()
            if task.finished:
                break
        else:
            pytest.fail("Task is taking too much time to finish")
        assert task.result == "ROTK9"

    async def job(executor):
        with pytest.raises(ZeroDivisionError):
            await ak.run_in_executor(executor, fail_eventually)

    with executor_cls() as executor:
        task = ak.start(job(executor))
        for _ in range(6):
            time.sleep(.5)
            kivy_runner.advance_a_frame()
            if task.finished:
                break
        else:
            pytest.fail("Task is taking too much time to finish")
