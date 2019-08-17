from kivy.app import App
from kivy.uix.label import Label
import asynckivy


class TestApp(App):

    def build(self):
        return Label(text='Hello', font_size='40sp')

    def on_start(self):
        async def animate_label(label):
            sleep = asynckivy.sleep
            await sleep(3)
            while True:
                label.text = 'This animation'
                await sleep(1)
                label.text = 'can be cancelled'
                await sleep(1)
                label.text = 'any time'
                await sleep(1)
                label.text = 'by touching the screen.'
                await sleep(1)
        label = self.root
        coro = animate_label(label)
        def on_touch_down(*__):
            coro.close()
            label.text = 'The animation was cancelled.'            
        label.bind(on_touch_down=on_touch_down)
        asynckivy.start(coro)


if __name__ == '__main__':
    TestApp().run()
