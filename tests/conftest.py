import pytest
from kivy.tests.fixtures import kivy_clock


@pytest.fixture()
def sleep_then_tick(kivy_clock):
    from functools import partial
    import time 

    def f(time_sleep, clock_time, clock_get_time, clock_tick, duration):
        # clock_get_time() returns the last time the clock ticked.
        # clock_time() returns the current time.
        time_sleep(clock_get_time() + duration - clock_time())
        clock_tick()

    return partial(f, time.sleep, kivy_clock.time, kivy_clock.get_time, kivy_clock.tick)
