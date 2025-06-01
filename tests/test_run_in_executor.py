import pytest
from concurrent.futures import ThreadPoolExecutor
import time
import threading


def test_thread_id(kivy_clock):
    import asynckivy as ak

    async def job(executor):
        before = threading.get_ident()
        await ak.run_in_executor(executor, lambda: None)
        after = threading.get_ident()
        assert before == after


    with ThreadPoolExecutor() as executor:
        task = ak.start(job(executor))
        time.sleep(.01)
        assert not task.finished
        kivy_clock.tick()
        assert task.finished


def test_propagate_exception(kivy_clock):
    import asynckivy as ak

    async def job(executor):
        with pytest.raises(ZeroDivisionError):
            await ak.run_in_executor(executor, lambda: 1 / 0)

    with ThreadPoolExecutor() as executor:
        task = ak.start(job(executor))
        time.sleep(.01)
        assert not task.finished
        kivy_clock.tick()
        assert task.finished


def test_no_exception(kivy_clock):
    import asynckivy as ak

    async def job(executor):
        assert 'A' == await ak.run_in_executor(executor, lambda: 'A')

    with ThreadPoolExecutor() as executor:
        task = ak.start(job(executor))
        time.sleep(.01)
        assert not task.finished
        kivy_clock.tick()
        assert task.finished


def test_cancel_before_start_executing(kivy_clock):
    import time
    import asynckivy as ak

    e = ak.StatefulEvent()

    async def job(executor):
        await ak.run_in_executor(executor, e.fire)

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(time.sleep, .1)
        task = ak.start(job(executor))
        time.sleep(.02)
        assert not task.finished
        assert not e.is_fired
        kivy_clock.tick()
        task.cancel()
        assert task.cancelled
        assert not e.is_fired
        time.sleep(.2)
        assert not e.is_fired
