from kivy.config import Config
Config.set('graphics', 'width', 100)
Config.set('graphics', 'height', 100)
from kivy.app import App
import asynckivy as ak
from asynckivy.queue import Queue


async def main():
    async def producer(name, q, items):
        for c in items:
            await q.put(c)
            print(name, "produced", c)
            await ak.sleep(.12)

    async def producers(*producers):
        # This function is necessary because you usually want to close the queue *after* all producers end.
        await ak.and_from_iterable(producers)
        q.close()

    async def consumer(name, q):
        async for c in q:
            print(name, "consumed", c)
            await ak.sleep(.08)

    from string import ascii_lowercase, ascii_uppercase
    q = Queue(capacity=None)
    await ak.and_(
        producers(
            producer('P1', q, ascii_lowercase),
            producer('P2', q, ascii_uppercase),
        ),
        consumer('C ', q),
    )
    print('Done all tasks')
    App.get_running_app().stop()


ak.start_soon(main())
App().run()
