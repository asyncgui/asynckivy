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
            await ak.sleep(.1)
        q.close()

    async def consumer(name, q):
        async for c in q:
            print(name, "consumed", c)
            await ak.sleep(.3)

    from string import ascii_lowercase
    q = Queue(capacity=None)
    await ak.wait_all(
        producer('P ', q, ascii_lowercase),
        consumer('C1', q),
        consumer('C2', q),
    )
    print('Done all tasks')
    App.get_running_app().stop()


main_task = ak.start(main())
App().run()
