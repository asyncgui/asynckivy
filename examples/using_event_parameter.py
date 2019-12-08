from kivy.app import App
from kivy.uix.label import Label
import asynckivy


class TestApp(App):

    def build(self):
        return Label(text='Hello', font_size='40sp')

    def on_start(self):
        async def handle_touch(label):
            sleep = asynckivy.sleep
            event = asynckivy.event
            await sleep(2)
            while True:
                label.text = 'Touch anywhere'
                __, touch = await event(label, 'on_touch_down')
                opos = label.to_window(*touch.opos)
                label.text = 'You touched at ' + str(tuple(int(v) for v in opos))
                await sleep(1)
        asynckivy.start(handle_touch(self.root))


if __name__ == '__main__':
    TestApp().run()