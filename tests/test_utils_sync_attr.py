import pytest


@pytest.fixture(scope='module')
def human_cls():
    from kivy.event import EventDispatcher
    from kivy.properties import NumericProperty

    class Human(EventDispatcher):
        age = NumericProperty(10)

    return Human


@pytest.fixture()
def human(human_cls):
    return human_cls()


def test_sync_attr(human):
    import types
    import asynckivy as ak

    obj = types.SimpleNamespace()
    with ak.sync_attr(from_=(human, 'age'), to_=(obj, 'AGE')):
        assert obj.AGE == 10
        human.age = 2
        assert obj.AGE == 2
        human.age = 0
        assert obj.AGE == 0
    human.age = 1
    assert obj.AGE == 0


def test_sync_attrs(human):
    import types
    import asynckivy as ak

    obj = types.SimpleNamespace()
    with ak.sync_attrs((human, 'age'), (obj, 'AGE'), (obj, 'age')):
        assert obj.AGE == 10
        assert obj.age == 10
        human.age = 2
        assert obj.AGE == 2
        assert obj.age == 2
        human.age = 0
        assert obj.AGE == 0
        assert obj.age == 0
    human.age = 1
    assert obj.AGE == 0
    assert obj.age == 0
