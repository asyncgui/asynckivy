import pytest


@pytest.fixture(scope="module")
def human_cls():
    from kivy.event import EventDispatcher
    from kivy.properties import NumericProperty

    class Human(EventDispatcher):
        age = NumericProperty(10)
    return Human


@pytest.fixture()
def human(human_cls):
    return human_cls()


def test_reenter(human):
    import types
    import asynckivy as ak

    obj = types.SimpleNamespace()
    with ak.smooth_attr(target=(human, "age"), follower=(obj, "AGE")) as cm:
        with pytest.raises(Exception):
            with cm:
                pass


def test_reuse(kivy_runner, human):
    import types
    import asynckivy as ak

    af = kivy_runner.advance_frame    
    obj = types.SimpleNamespace(AGE=0)
    with ak.smooth_attr(target=(human, "age"), follower=(obj, "AGE")) as cm:
        af(dt=0.2)
        af(dt=0.2)
    assert obj.AGE == 10
    obj.AGE = 0
    with cm:
        af(dt=0.2)
        af(dt=0.2)
    assert obj.AGE == 10
