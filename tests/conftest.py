import pytest
from kivy.tests.fixtures import kivy_clock


@pytest.fixture()
def sleep_then_tick(virtual_kivy_clock):
    def sleep_then_tick(duration):
        virtual_kivy_clock.sleep(duration)
        virtual_kivy_clock.tick()
    return sleep_then_tick


@pytest.fixture()
def virtual_kivy_clock(kivy_clock):
    current_time = kivy_clock.time()
    kivy_clock.time = lambda: current_time

    def sleep(duration):
        nonlocal current_time
        current_time += duration

    kivy_clock.sleep = sleep
    return kivy_clock
