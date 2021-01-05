import pytest


def test_propagate_an_uncaught_exception_to_the_caller():
    import time
    from kivy.clock import Clock
    import asynckivy as ak

    def impolite_func():
        return 1 / 0

    async def job():
        with pytest.raises(ZeroDivisionError):
            await ak.run_in_thread(impolite_func, polling_interval=.1)
        nonlocal done; done = True

    done = False
    ak.start(job())
    time.sleep(.2)
    Clock.tick()
    assert done
