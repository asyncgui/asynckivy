import pytest


@pytest.fixture(autouse=True)
def unlimit_maxfps(monkeypatch):
    from kivy.clock import Clock
    monkeypatch.setattr(Clock, '_max_fps', 0)


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


class Target:
    def __init__(self):
        self.num = 0
        self.lst = [0, 0, ]
        self.dct = {'key': 0, }


class Clock:
    def __init__(self):
        self.reset()
    def reset(self):
        from time import time
        from kivy.clock import Clock
        self.last = time()
        Clock.tick()
    def sleep(self, duration):
        from time import time, sleep
        from kivy.clock import Clock
        self.last = next = self.last + duration
        sleep(next - time())
        Clock.tick()


@pytest.mark.parametrize('force_final_value', (True, False, ))
def test_cancel(approx, force_final_value):
    import asynckivy as ak
    target = Target()
    coro = ak.animate(
        target, num=100, d=.4, force_final_value=force_final_value)
    clock = Clock()
    ak.start(coro)

    clock.sleep(.1)
    assert target.num == approx(25)
    clock.sleep(.1)
    assert target.num == approx(50)
    coro.close()  # cancel
    if force_final_value:
        assert target.num == approx(100)
    else:
        assert target.num == approx(50)


def test_list(approx):
    import asynckivy as ak
    target = Target()
    coro = ak.animate(target, lst=[100, 200], d=.4)
    clock = Clock()
    ak.start(coro)

    clock.sleep(.1)
    assert target.lst == approx([25, 50])
    clock.sleep(.1)
    assert target.lst == approx([50, 100])
    clock.sleep(.1)
    assert target.lst == approx([75, 150])
    clock.sleep(.1)
    assert target.lst == approx([100, 200])


def test_dict(approx):
    import asynckivy as ak
    target = Target()
    coro = ak.animate(target, dct={'key': 100}, d=.4)
    clock = Clock()
    ak.start(coro)

    clock.sleep(.1)
    assert target.dct == approx({'key': 25})
    clock.sleep(.1)
    assert target.dct == approx({'key': 50})
    clock.sleep(.1)
    assert target.dct == approx({'key': 75})
    clock.sleep(.1)
    assert target.dct == approx({'key': 100})
