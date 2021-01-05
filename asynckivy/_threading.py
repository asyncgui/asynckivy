__all__ = ('run_in_thread', )


async def run_in_thread(func, *, daemon=False, polling_interval=3):
    from threading import Thread
    from ._sleep import create_sleep

    return_value = None
    done = False
    exception = None

    def wrapper():
        nonlocal return_value, done, exception
        try:
            return_value = func()
        except Exception as e:
            exception = e
        finally:
            done = True

    Thread(target=wrapper, daemon=daemon).start()
    sleep = await create_sleep(polling_interval)
    while not done:
        await sleep()
    if exception is not None:
        raise exception
    return return_value
