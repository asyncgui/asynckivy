from kivy.app import App
import asynckivy as ak
from asynckivy.queue import Queue


async def main():
    async def producer(q, items):
        for c in items:
            await q.put(c)
            print("produced    :", c)
        q.close()

    async def consumer(q, name):
        async for c in q:
            print(f"consumed ({name}):", c)

    from string import ascii_uppercase
    q = Queue()
    await ak.and_(
        producer(q, ascii_uppercase),
        consumer(q, 'A'),
        consumer(q, 'B'),
    )
    print('Done all tasks')
    App.get_running_app().stop()


ak.start_soon(main())
App().run()
