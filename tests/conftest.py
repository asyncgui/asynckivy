import pytest
from kivy.tests.fixtures import kivy_clock


@pytest.fixture()
def ready_to_sleep():
    from kivy.clock import Clock
    from time import time, sleep

    last = None

    def sleep_then_tick(duration):
        nonlocal last
        last += duration
        sleep(last - time())
        Clock.tick()

    def ready_to_sleep():
        nonlocal last
        Clock.tick()
        last = time()
        return sleep_then_tick

    return ready_to_sleep
