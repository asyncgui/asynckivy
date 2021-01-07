from kivy.config import Config
Config.set('graphics', 'maxfps', 0)
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak


KV_CODE = '''
BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    ToggleButton:
        text: 'Clock.schedule_interval(lambda __: None, 0)'
        group: 'aaa'
        on_press:
            app.reset()
            if self.state == 'down': app.start_ver_schedule_interval()
    ToggleButton:
        text:'while True:\\n    await sleep(0)'
        group: 'aaa'
        on_press:
            app.reset()
            if self.state == 'down': app.start_ver_sleep()
    ToggleButton:
        text: 'sleep = await create_sleep(0)\\nwhile True:\\n    await sleep()'
        group: 'aaa'
        on_press:
            app.reset()
            if self.state == 'down': app.start_ver_create_sleep()
'''


class SampleApp(App):
    coro = None

    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        def print_fps(dt):
            print(Clock.get_fps(), 'fps')
        Clock.schedule_interval(print_fps, 1)

    def reset(self):
        coro = self.coro
        if coro is not None:
            coro.close()
        self.coro = None

    def start_ver_schedule_interval(self):
        print('---- start ver schedule_interval() ----')

        async def async_fn():
            clock_event = Clock.schedule_interval(lambda __: None, 0)
            try:
                await ak.sleep_forever()
            finally:
                clock_event.cancel()
        self.coro = async_fn()
        ak.start(self.coro)

    def start_ver_sleep(self):
        print('---- start ver sleep() ----')

        async def async_fn():
            sleep = ak.sleep
            while True:
                await sleep(0)
        self.coro = async_fn()
        ak.start(self.coro)

    def start_ver_create_sleep(self):
        print('---- start ver create_sleep() ----')

        async def async_fn():
            sleep = await ak.create_sleep(0)
            while True:
                await sleep()
        self.coro = async_fn()
        ak.start(self.coro)


if __name__ == '__main__':
    SampleApp().run()
