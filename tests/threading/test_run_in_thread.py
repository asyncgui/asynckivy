import pytest
import threading
import time


@pytest.mark.parametrize('daemon', (True, False))
def test_thread_id(daemon):
    from kivy.clock import Clock
    import asynckivy as ak

    async def job():
        before = threading.get_ident()
        await ak.run_in_thread(lambda: None, daemon=daemon)
        after = threading.get_ident()
        assert before == after

    task = ak.start(job())
    time.sleep(.01)
    assert not task.done
    Clock.tick()
    assert task.done


@pytest.mark.parametrize('daemon', (True, False))
def test_propagate_exception(daemon):
    from kivy.clock import Clock
    import asynckivy as ak

    async def job():
        with pytest.raises(ZeroDivisionError):
            await ak.run_in_thread(lambda: 1 / 0, daemon=daemon)

    task = ak.start(job())
    time.sleep(.01)
    assert not task.done
    Clock.tick()
    assert task.done


@pytest.mark.parametrize('daemon', (True, False))
def test_no_exception(daemon):
    from kivy.clock import Clock
    import asynckivy as ak

    async def job():
        assert 'A' == await ak.run_in_thread(lambda: 'A', daemon=daemon)

    task = ak.start(job())
    time.sleep(.01)
    assert not task.done
    Clock.tick()
    assert task.done
