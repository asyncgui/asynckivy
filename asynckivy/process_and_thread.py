__all__ = ('thread', 'process', )


async def thread(func, *, daemon=False, polling_interval=3):
    from threading import Thread
    from ._sleep import sleep

    return_value = None
    is_finished = False
    def wrapper():
        nonlocal return_value, is_finished
        return_value = func()
        is_finished = True
    Thread(target=wrapper, daemon=daemon).start()
    while not is_finished:
        await sleep(polling_interval)
    return return_value


async def process(p, *, polling_interval=3):
    '''wait for the completion of subprocess'''
    from ._sleep import sleep

    while p.poll() is None:
        await sleep(polling_interval)
    return p.returncode
