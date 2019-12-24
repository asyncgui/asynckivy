from kivy.app import App
from kivy.uix.button import Button
import asynckivy as ak


class TestApp(App):

    def build(self):
        return Button(font_size='20sp')

    def on_start(self):
        async def some_task():
            from subprocess import Popen
            button = self.root
            button.text = 'start `ls -l`'
            await ak.event(button, 'on_press')
            button.text = 'running...'
            p = Popen(('ls', '-l',))
            returncode = await ak.process(p)
            button.text = f'return code: {returncode}'
        ak.start(some_task())


if __name__ == '__main__':
    TestApp().run()
