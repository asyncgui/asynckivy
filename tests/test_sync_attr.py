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


p_eager = pytest.mark.parametrize("eager", [False, True])


@p_eager
def test_sync_attr_reuse(human, eager):
    import types
    import asynckivy as ak

    obj = types.SimpleNamespace()
    with ak.sync_attr(from_=(human, "age"), to_=(obj, "AGE"), eager=eager) as cm:
        if eager:
            assert obj.AGE == 10
        else:
            assert not hasattr(obj, "AGE")
        human.age = 2
        assert obj.AGE == 2
        human.age = 0
        assert obj.AGE == 0
    human.age = 1
    assert obj.AGE == 0

    # reuse
    with cm:
        human.age = 3
        assert obj.AGE == 3


@p_eager
def test_sync_attr_reenter(human, eager):
    import types
    import asynckivy as ak

    obj = types.SimpleNamespace()
    with ak.sync_attr(from_=(human, "age"), to_=(obj, "AGE"), eager=eager) as cm:
        with pytest.raises(ak.RecursiveActivationError):
            with cm:
                pass


@p_eager
def test_sync_attrs_reuse(human, eager):
    import types
    import asynckivy as ak

    obj = types.SimpleNamespace()
    with ak.sync_attrs((human, "age"), (obj, "AGE"), (obj, "age"), eager=eager) as cm:
        if eager:
            assert obj.AGE == 10
            assert obj.age == 10
        else:
            assert not hasattr(obj, "AGE")
            assert not hasattr(obj, "age")
        human.age = 2
        assert obj.AGE == 2
        assert obj.age == 2
        human.age = 0
        assert obj.AGE == 0
        assert obj.age == 0
    human.age = 1
    assert obj.AGE == 0
    assert obj.age == 0

    # reuse
    with cm:
        human.age = 3
        assert obj.AGE == 3
        assert obj.age == 3


@p_eager
def test_sync_attrs_reenter(human, eager):
    import types
    import asynckivy as ak

    obj = types.SimpleNamespace()
    with ak.sync_attrs((human, "age"), (obj, "AGE"), (obj, "age"), eager=eager) as cm:
        with pytest.raises(ak.RecursiveActivationError):
            with cm:
                pass
