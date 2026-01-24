import pytest


@pytest.fixture(scope="module", autouse=True)
def _shorten_gc_interval():
    from asynckivy import _managed_start as _ms
    original = _ms._GC_IN_EVERY
    _ms._GC_IN_EVERY = _ms._n_until_gc = 2
    yield
    _ms._GC_IN_EVERY = _ms._n_until_gc = original


@pytest.fixture(autouse=True)
def _cancel_managed_tasks():
    import asynckivy as ak
    ak.cancel_managed_tasks()
    yield
    ak.cancel_managed_tasks()


async def finish_immediately():
    pass


def test_finished_tasks_only():
    import asynckivy as ak
    from asynckivy import _managed_start as _ms

    assert len(_ms._managed_tasks) == 0
    assert _ms._n_until_gc == 2
    ak.managed_start(finish_immediately())
    assert len(_ms._managed_tasks) == 1
    assert _ms._n_until_gc == 1
    ak.managed_start(finish_immediately())
    assert len(_ms._managed_tasks) == 0
    assert _ms._n_until_gc == 2


def test_unfinished_tasks_only():
    import asynckivy as ak
    from asynckivy import _managed_start as _ms

    assert len(_ms._managed_tasks) == 0
    ak.managed_start(ak.sleep_forever())
    assert len(_ms._managed_tasks) == 1
    ak.managed_start(ak.sleep_forever())
    assert len(_ms._managed_tasks) == 2
    assert _ms._n_until_gc == _ms._GC_IN_EVERY


def test_mix_finished_tasks_and_unfinished_ones():
    import asynckivy as ak
    from asynckivy import _managed_start as _ms

    assert len(_ms._managed_tasks) == 0
    ak.managed_start(ak.sleep_forever())
    assert len(_ms._managed_tasks) == 1
    ak.managed_start(finish_immediately())
    assert len(_ms._managed_tasks) == 1
    assert _ms._n_until_gc == _ms._GC_IN_EVERY
