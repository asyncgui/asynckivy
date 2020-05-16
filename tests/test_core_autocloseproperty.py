import pytest


@pytest.fixture(scope='module')
def owner_cls():
    from asynckivy import AutoCloseProperty
    class Owner:
        coro = AutoCloseProperty()
    return Owner


@pytest.fixture()
def owner(owner_cls):
    return owner_cls()


async def async_fn():
    pass


def test_owner_cls(owner_cls):
    from asynckivy import AutoCloseProperty
    assert type(owner_cls.coro) is AutoCloseProperty
    assert owner_cls.coro.name == 'coro'


def test_initial_state(owner):
    assert owner.coro is None
    assert 'coro' not in owner.__dict__


def test_set(owner):
    from inspect import getcoroutinestate, CORO_CLOSED, CORO_CREATED
    owner.coro = coro1 = async_fn()
    assert getcoroutinestate(coro1) == CORO_CREATED
    assert owner.coro is coro1
    assert owner.__dict__['coro'] is coro1
    owner.coro = coro2 = async_fn()
    assert getcoroutinestate(coro1) == CORO_CLOSED
    assert getcoroutinestate(coro2) == CORO_CREATED
    assert owner.coro is coro2
    assert owner.__dict__['coro'] is coro2
    owner.coro = None
    assert getcoroutinestate(coro1) == CORO_CLOSED
    assert getcoroutinestate(coro2) == CORO_CLOSED
    assert owner.coro is None
    assert owner.__dict__['coro'] is None


def test_setting_the_same_value_does_not_trigger_close(owner):
    from inspect import getcoroutinestate, CORO_CREATED
    owner.coro = coro1 = async_fn()
    owner.coro = coro1
    assert getcoroutinestate(coro1) == CORO_CREATED


def test_delete(owner):
    from inspect import getcoroutinestate, CORO_CLOSED
    owner.coro = coro = async_fn()
    del owner.coro
    assert getcoroutinestate(coro) == CORO_CLOSED
    assert 'coro' not in owner.__dict__
