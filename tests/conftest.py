import pytest
from kivy.tests.fixtures import kivy_clock


@pytest.fixture(scope='session')
def _sleep_then_tick():
    from functools import partial
    from kivy.clock import Clock
    import time 

    def f(time_sleep, clock_time, clock_get_time, clock_tick, duration):
        # clock_get_time() returns the last time the clock ticked.
        # clock_time() returns the current time.
        time_sleep(clock_get_time() + duration - clock_time())
        clock_tick()

    return partial(f, time.sleep, Clock.time, Clock.get_time, Clock.tick)


@pytest.fixture()
def sleep_then_tick(_sleep_then_tick):
    from kivy.clock import Clock
    Clock.tick()
    return _sleep_then_tick
