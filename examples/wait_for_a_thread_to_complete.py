'''
A simple example of using ``asynckivy.run_in_thread()``.
'''

from kivy.app import App
from kivy.uix.button import Button
import asynckivy as ak


def heavy_task(n):
    import time
    for i in range(n):
        time.sleep(1)
        print('heavy task:', i)


class TestApp(App):

    def build(self):
        return Button(font_size='20sp')

    def on_start(self):
        ak.start(self.main())

    async def main(self):
        button = self.root
        button.text = 'start heavy task'
        await ak.event(button, 'on_press')
        button.text = 'running...'
        await ak.run_in_thread(lambda: heavy_task(5))
        button.text = 'done'


if __name__ == '__main__':
    TestApp().run()
