import pytest


@pytest.fixture(scope='module')
def owner_cls():
    from asynckivy import CloseableProperty
    class Owner:
        coro1 = CloseableProperty()
        coro2 = CloseableProperty()
    return Owner


@pytest.fixture()
def owner(owner_cls):
    return owner_cls()


async def async_fn():
    pass


def test_owner_cls(owner_cls):
    from asynckivy import CloseableProperty
    assert type(owner_cls.coro1) is CloseableProperty
    assert type(owner_cls.coro2) is CloseableProperty
    assert owner_cls.coro1.name == 'coro1'
    assert owner_cls.coro2.name == 'coro2'


def test_initial_state(owner):
    assert owner.coro1 is None
    assert owner.coro2 is None
    assert 'coro1' not in owner.__dict__
    assert 'coro2' not in owner.__dict__


def test_set(owner):
    from inspect import getcoroutinestate, CORO_CLOSED, CORO_CREATED
    owner.coro1 = coro1a = async_fn()
    owner.coro2 = coro2 = async_fn()
    assert owner.coro1 is coro1a
    assert owner.coro2 is coro2
    assert owner.__dict__['coro1'] is coro1a
    assert owner.__dict__['coro2'] is coro2
    owner.coro1 = coro1b = async_fn()
    assert getcoroutinestate(coro1a) == CORO_CLOSED
    assert getcoroutinestate(coro2) == CORO_CREATED
    assert owner.coro1 is coro1b
    assert owner.coro2 is coro2
    assert owner.__dict__['coro1'] is coro1b
    assert owner.__dict__['coro2'] is coro2
    owner.coro1 = None
    assert getcoroutinestate(coro1b) == CORO_CLOSED
    assert getcoroutinestate(coro2) == CORO_CREATED
    assert owner.coro1 is None
    assert owner.coro2 is coro2
    assert owner.__dict__['coro1'] is None
    assert owner.__dict__['coro2'] is coro2


def test_delete(owner):
    from inspect import getcoroutinestate, CORO_CLOSED, CORO_CREATED
    owner.coro1 = coro1 = async_fn()
    owner.coro2 = coro2 = async_fn()
    del owner.coro1
    assert getcoroutinestate(coro1) == CORO_CLOSED
    assert getcoroutinestate(coro2) == CORO_CREATED
    assert 'coro1' not in owner.__dict__
    assert owner.__dict__['coro2'] is coro2
