import types
import typing
import asynckivy as ak


class Task:
    __slots__ = ('coro', 'done', 'result', '_done_callback')
    def __init__(self, coro, *, done_callback=None):
        self.coro = coro
        self.done = False
        self.result = None
        self._done_callback = done_callback
    async def _run(self):
        self.result = await self.coro
        self.done = True
        if self._done_callback is not None:
            self._done_callback()


@types.coroutine
def gather(coros:typing.Iterable[typing.Coroutine], *, n:int=None) -> typing.Sequence[Task]:
    coros = tuple(coros)
    n_coros_left = n if n is not None else len(coros)
    step_coro = None

    def done_callback():
        nonlocal n_coros_left
        n_coros_left -= 1
        if n_coros_left == 0:
            step_coro()
    tasks = tuple(Task(coro, done_callback=done_callback) for coro in coros)
    for task in tasks:
        ak.start(task._run())

    def callback(step_coro_):
        nonlocal step_coro
        step_coro = step_coro_
    yield callback

    return tasks


async def or_(*coros):
    return await gather(coros, n=1)


async def and_(*coros):
    return await gather(coros)



def _test():
    import textwrap
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.factory import Factory
    
    KV_CODE = textwrap.dedent('''
    <Label>:
        font_size: '24sp'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            id: label
            size_hint_y: None
            height: max(sp(24), self.texture_size[1])
        BoxLayout:
            id: layout
            spacing: 10
            Button:
                text: 'A'
            Button:
                text: 'B'
            Button:
                text: 'C'
    ''')
    
    class TestApp(App):
        def build(self):
            return Builder.load_string(KV_CODE)
        def on_start(self):
            import itertools
            import asynckivy as ak
            ids = self.root.ids
            label = ids.label
            buttons = list(reversed(ids.layout.children))
            async def test_await_multiple_coroutines():
                # ----------------------------------------------------
                # wait for the completion of any number of coroutines
                # ----------------------------------------------------
                label.text = f'wait until 2 of {len(buttons)} buttons are pressed'
                tasks = await gather(
                    (ak.event(button, 'on_press') for button in buttons),
                    n=2
                )
                label.text = 'Done! ({} and {} were pressed)'.format(
                    *[task.result[0][0].text for task in tasks if task.done]
                )
                await ak.sleep(1)
                label.text = 'next'
                await ak.sleep(1)

                # -----------------------------------------
                # wait for the completion of one coroutine 
                # -----------------------------------------
                label.text = "wait until button'A' is pressed or 5s passes"
                tasks = await or_(
                    ak.event(buttons[0], 'on_press'),
                    ak.sleep(5),
                )
                label.text = 'Done! ({})'.format(
                    "button'A' was pressed" if tasks[0].done else "5s passed"
                )
                await ak.sleep(1)
                label.text = 'next'
                await ak.sleep(1)

                # ------------------------------------------
                # wait for the completion of all coroutines
                # ------------------------------------------
                label.text = "wait until all buttons are pressed and 5s passes"
                tasks = await and_(
                    ak.sleep(5),
                    *(ak.event(button, 'on_press') for button in buttons)
                )
                label.text = 'Done!'
                await ak.sleep(2)

            ak.start(test_await_multiple_coroutines())
            
    TestApp().run()


if __name__ == '__main__':
    _test()
    