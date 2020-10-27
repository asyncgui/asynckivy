import pytest


def test_invalid_argument():
    import asynckivy as ak
    async def job():
        async with ak.fade_transition(unknown=True):
            pass
    with pytest.raises(ValueError):
        ak.start(job())
