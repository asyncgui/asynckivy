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
        async def some_task():
            button = self.root
            button.text = 'start heavy task'
            await ak.event(button, 'on_press')
            button.text = 'running...'
            await ak.run_in_thread(lambda: heavy_task(5))
            button.text = 'done'
        ak.start(some_task())


if __name__ == '__main__':
    TestApp().run()
