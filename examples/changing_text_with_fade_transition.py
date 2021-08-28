'''
A simple usecase of ``asynckivy.fade_transition()``.
'''

from kivy.app import App
from kivy.uix.label import Label
import asynckivy as ak


class TestApp(App):
    def build(self):
        return Label(font_size=40)

    def on_start(self):
        async def main_task(label):
            from kivy.utils import get_random_color
            await ak.n_frames(4)
            for text in (
                'Zen of Python',
                'Beautiful is better than ugly.',
                'Explicit is better than implicit.',
                'Simple is better than complex.',
                'Complex is better than complicated.',
                '',
            ):
                async with ak.fade_transition(label):
                    label.text = text
                    label.color = get_random_color()
                await ak.event(label, 'on_touch_down')
            self.stop()
        ak.start(main_task(self.root))


if __name__ == '__main__':
    TestApp().run()
