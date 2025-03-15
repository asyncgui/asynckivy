import pytest
from kivy.tests.fixtures import kivy_clock


@pytest.fixture()
def sleep_then_tick(kivy_clock):
    current_time = kivy_clock.time()
    kivy_clock.time = lambda: current_time

    def sleep_then_tick(duration):
        nonlocal current_time
        current_time += duration
        kivy_clock.tick()
    return sleep_then_tick
