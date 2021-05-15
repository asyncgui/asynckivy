import pytest
from concurrent.futures import ThreadPoolExecutor
import time
import threading


def test_thread_id():
    from kivy.clock import Clock
    import asynckivy as ak

    async def job(executer):
        before = threading.get_ident()
        await ak.run_in_executer(lambda: None, executer)
        after = threading.get_ident()
        assert before == after


    with ThreadPoolExecutor() as executer:
        task = ak.start(job(executer))
        time.sleep(.01)
        assert not task.done
        Clock.tick()
        assert task.done


def test_propagate_exception():
    from kivy.clock import Clock
    import asynckivy as ak

    async def job(executer):
        with pytest.raises(ZeroDivisionError):
            await ak.run_in_executer(lambda: 1 / 0, executer)

    with ThreadPoolExecutor() as executer:
        task = ak.start(job(executer))
        time.sleep(.01)
        assert not task.done
        Clock.tick()
        assert task.done


def test_no_exception():
    from kivy.clock import Clock
    import asynckivy as ak

    async def job(executer):
        assert 'A' == await ak.run_in_executer(lambda: 'A', executer)

    with ThreadPoolExecutor() as executer:
        task = ak.start(job(executer))
        time.sleep(.01)
        assert not task.done
        Clock.tick()
        assert task.done


def test_cancel_before_getting_excuted():
    import time
    from kivy.clock import Clock
    import asynckivy as ak

    flag = ak.Event()

    async def job(executer):
        await ak.run_in_executer(flag.set, executer)

    with ThreadPoolExecutor(max_workers=1) as executer:
        executer.submit(time.sleep, .1)
        task = ak.start(job(executer))
        time.sleep(.02)
        assert not task.done
        assert not flag.is_set()
        Clock.tick()
        task.cancel()
        assert task.cancelled
        assert not flag.is_set()
        time.sleep(.2)
        assert not flag.is_set()
