'''
A simple usecase of ``asynckivy.interpolate()``.
'''

from kivy.app import App
from kivy.uix.label import Label
import asynckivy as ak


class TestApp(App):

    def build(self):
        return Label()

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        label = self.root
        await ak.n_frames(4)
        async for font_size in ak.interpolate(start=0, end=300, duration=5, step=.1, transition='out_cubic'):
            label.font_size = font_size
            label.text = str(int(font_size))


if __name__ == '__main__':
    TestApp().run()
