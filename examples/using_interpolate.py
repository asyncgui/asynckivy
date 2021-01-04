'''
A simple usucase of ``asynckivy.interpolate()``.
'''

from kivy.app import App
from kivy.uix.label import Label
import asynckivy as ak


class TestApp(App):

    def build(self):
        return Label()

    def on_start(self):
        async def animate_label(label):
            await ak.sleep(0)
            await ak.sleep(1)
            async for font_size in ak.interpolate(
                    start=0, end=300, d=5, s=.1, t='out_cubic'):
                label.font_size = font_size
                label.text = str(int(font_size))
        ak.start(animate_label(self.root))


if __name__ == '__main__':
    TestApp().run()
