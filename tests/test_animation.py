import pytest


@pytest.fixture(scope='module')
def approx():
    from functools import partial
    return partial(pytest.approx, abs=1)


class Target:
    def __init__(self):
        self.num = 0
        self.lst = [0, 0, ]
        self.dct = {'key': 0, }


def test_cancel(approx, ready_to_sleep):
    import asynckivy as ak
    target = Target()
    coro = ak.animate(target, num=100, d=.4,)
    sleep = ready_to_sleep()
    ak.raw_start(coro)

    sleep(.1)
    assert target.num == approx(25)
    sleep(.1)
    assert target.num == approx(50)
    coro.close()  # cancel
    assert target.num == approx(50)


def test_list(approx, ready_to_sleep):
    import asynckivy as ak
    target = Target()
    coro = ak.animate(target, lst=[100, 200], d=.4)
    sleep = ready_to_sleep()
    ak.start(coro)

    sleep(.1)
    assert target.lst == approx([25, 50])
    sleep(.1)
    assert target.lst == approx([50, 100])
    sleep(.1)
    assert target.lst == approx([75, 150])
    sleep(.1)
    assert target.lst == approx([100, 200])
    sleep(.1)
    assert target.lst == approx([100, 200])


def test_dict(approx, ready_to_sleep):
    import asynckivy as ak
    target = Target()
    coro = ak.animate(target, dct={'key': 100}, d=.4)
    sleep = ready_to_sleep()
    ak.start(coro)

    sleep(.1)
    assert target.dct == approx({'key': 25})
    sleep(.1)
    assert target.dct == approx({'key': 50})
    sleep(.1)
    assert target.dct == approx({'key': 75})
    sleep(.1)
    assert target.dct == approx({'key': 100})
    sleep(.1)
    assert target.dct == approx({'key': 100})
