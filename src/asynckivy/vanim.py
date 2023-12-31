__all__ = (
    'dt', 'delta_time',
    'et', 'elapsed_time',
    'dt_et', 'delta_time_elapsed_time',
    'progress',
    'dt_et_progress', 'delta_time_elapsed_time_progress',
)

from asynckivy import repeat_sleeping


async def dt(*, step=0):
    async with repeat_sleeping(step=step) as sleep:
        while True:
            yield await sleep()


async def et(*, step=0):
    et = 0.
    async with repeat_sleeping(step=step) as sleep:
        while True:
            et += await sleep()
            yield et


async def dt_et(*, step=0):
    et = 0.
    async with repeat_sleeping(step=step) as sleep:
        while True:
            dt = await sleep()
            et += dt
            yield dt, et


async def progress(*, duration=1., step=0):
    et = 0.
    async with repeat_sleeping(step=step) as sleep:
        while et < duration:
            et += await sleep()
            yield et / duration


async def dt_et_progress(*, duration=1., step=0):
    et = 0.
    async with repeat_sleeping(step=step) as sleep:
        while et < duration:
            dt = await sleep()
            et += dt
            yield dt, et, et / duration


# alias
delta_time = dt
elapsed_time = et
delta_time_elapsed_time = dt_et
delta_time_elapsed_time_progress = dt_et_progress
