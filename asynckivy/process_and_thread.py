__all__ = ('thread', 'process', )


async def thread(func, *, daemon=False, polling_interval=3):
    from threading import Thread
    from ._sleep import create_sleep

    return_value = None
    is_finished = False
    def wrapper():
        nonlocal return_value, is_finished
        return_value = func()
        is_finished = True
    Thread(target=wrapper, daemon=daemon).start()
    sleep = await create_sleep(polling_interval)
    while not is_finished:
        await sleep()
    return return_value


async def process(p, *, polling_interval=3):
    '''wait for the completion of subprocess'''
    from ._sleep import create_sleep

    sleep = await create_sleep(polling_interval)
    poll = p.poll
    while poll() is None:
        await sleep()
    return p.returncode
