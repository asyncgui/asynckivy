import pytest
from concurrent.futures import ThreadPoolExecutor
import time
import threading


def test_thread_id(kivy_clock):
    import asynckivy as ak

    async def job(executer):
        before = threading.get_ident()
        await ak.run_in_executer(executer, lambda: None)
        after = threading.get_ident()
        assert before == after


    with ThreadPoolExecutor() as executer:
        task = ak.start(job(executer))
        time.sleep(.01)
        assert not task.finished
        kivy_clock.tick()
        assert task.finished


def test_propagate_exception(kivy_clock):
    import asynckivy as ak

    async def job(executer):
        with pytest.raises(ZeroDivisionError):
            await ak.run_in_executer(executer, lambda: 1 / 0)

    with ThreadPoolExecutor() as executer:
        task = ak.start(job(executer))
        time.sleep(.01)
        assert not task.finished
        kivy_clock.tick()
        assert task.finished


def test_no_exception(kivy_clock):
    import asynckivy as ak

    async def job(executer):
        assert 'A' == await ak.run_in_executer(executer, lambda: 'A')

    with ThreadPoolExecutor() as executer:
        task = ak.start(job(executer))
        time.sleep(.01)
        assert not task.finished
        kivy_clock.tick()
        assert task.finished


def test_cancel_before_getting_excuted(kivy_clock):
    import time
    import asynckivy as ak

    flag = ak.Event()

    async def job(executer):
        await ak.run_in_executer(executer, flag.set)

    with ThreadPoolExecutor(max_workers=1) as executer:
        executer.submit(time.sleep, .1)
        task = ak.start(job(executer))
        time.sleep(.02)
        assert not task.finished
        assert not flag.is_set
        kivy_clock.tick()
        task.cancel()
        assert task.cancelled
        assert not flag.is_set
        time.sleep(.2)
        assert not flag.is_set
