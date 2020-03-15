def test_sleep():
    import time
    from kivy.clock import Clock
    import asynckivy as ak
    async def _test():
        await ak.sleep(.1)
        nonlocal done;done = True
    done = False
    Clock.tick()
    ak.start(_test())
    assert not done
    Clock.tick()
    assert not done
    time.sleep(.07)
    Clock.tick()
    assert not done
    time.sleep(.07)
    Clock.tick()
    assert done


def test_sleep_free():
    import time
    from kivy.clock import Clock
    import asynckivy as ak
    async def _test():
        await ak.sleep_free(.1)
        nonlocal done;done = True
    done = False
    Clock.tick()
    ak.start(_test())
    assert not done
    Clock.tick()
    assert not done
    time.sleep(.07)
    Clock.tick()
    assert not done
    time.sleep(.07)
    Clock.tick()
    assert done
