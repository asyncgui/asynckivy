'''
Implementing :func:`trio.move_on_after()`.
'''

from kivy.app import App
from kivy.uix.label import Label
import asynckivy as ak


def move_on_after(seconds: float):
    '''
    Similar to :func:`trio.move_on_after`.
    The difference is this one returns an async context manager not a regular one.
    '''
    return ak.wait_any_cm(ak.sleep(seconds))


class TestApp(App):

    def build(self):
        return Label(font_size="200sp")

    def on_start(self):
        ak.start(self.main())

    async def main(self):
        label = self.root
        await ak.n_frames(2)
        async with move_on_after(3):
            while True:
                label.text = 'A'
                await ak.sleep(.4)
                label.text = 'B'
                await ak.sleep(.4)
                label.text = 'C'
                await ak.sleep(.4)
        label.text = "fin"
        label.italic = True


if __name__ == '__main__':
    TestApp(title="trio.move_on_after()").run()
