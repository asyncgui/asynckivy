from kivy.config import Config
Config.set('graphics', 'maxfps', 0)
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak


KV_CODE = '''
<MyToggleButton@ToggleButton>:
    group: 'aaa'
    font_size: '20sp'
    on_state: if args[1] == 'down': app.measure_fps(self.text)
    allow_no_selection: False

BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    MyToggleButton:
        text: 'schedule_interval'
    MyToggleButton:
        text:'sleep'
    MyToggleButton:
        text: 'repeat_sleeping'
    MyToggleButton:
        text: 'anim_with_dt'
    MyToggleButton:
        text: 'anim_with_dt_et'
'''


class SampleApp(App):
    def build(self):
        self._tasks = []
        return Builder.load_string(KV_CODE)

    def on_start(self):
        def print_fps(dt, print=print, get_fps=Clock.get_fps):
            print(get_fps(), 'fps')
        Clock.schedule_interval(print_fps, 1)

    def measure_fps(self, type):
        print('---- start measuring ----', type)
        async_func = globals()['ver_' + type]
        for task in self._tasks:
            task.cancel()
        self._tasks = [ak.start(async_func()) for __ in range(100)]


async def ver_schedule_interval():
    clock_event = Clock.schedule_interval(lambda __: None, 0)
    try:
        await ak.sleep_forever()
    finally:
        clock_event.cancel()


async def ver_sleep():
    sleep = ak.sleep
    while True:
        await sleep(0)


async def ver_repeat_sleeping():
    async with ak.repeat_sleeping(step=0) as sleep:
        while True:
            await sleep()


async def ver_anim_with_dt():
    async for dt in ak.anim_with_dt():
        pass


async def ver_anim_with_dt_et():
    async for dt, et in ak.anim_with_dt_et():
        pass


if __name__ == '__main__':
    SampleApp().run()
