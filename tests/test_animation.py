import pytest


@pytest.fixture(autouse=True)
def unlimit_maxfps(monkeypatch):
    from kivy.clock import Clock
    monkeypatch.setattr(Clock, '_max_fps', 0)


@pytest.fixture(scope='module')
def point_cls():
    from dataclasses import dataclass
    @dataclass
    class Point:
        x: int = 0
        y: int = 0
    return Point


@pytest.fixture()
def point(point_cls):
    return point_cls()


def test_skip(point):
    from math import isclose
    import time
    from kivy.clock import Clock
    import asynckivy as ak

    Clock.tick()
    coro = ak.animation(point, x=100, d=1, force_final_value=True)
    ak.start(coro)

    time.sleep(.2)
    Clock.tick()
    assert isclose(point.x, 20, abs_tol=1)
    time.sleep(.2)
    Clock.tick()
    assert isclose(point.x, 40, abs_tol=1)
    coro.close()
    assert point.x == 100
