from kivy.config import Config
Config.set('graphics', 'maxfps', 0)
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak

import types

KV_CODE = '''
<MyToggleButton@ToggleButton>:
    group: 'aaa'
    on_press: if self.state == 'down': app.measure_fps(self.text)

BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    MyToggleButton:
        text: 'original'
    MyToggleButton:
        text: 'new1'
    MyToggleButton:
        text: 'new2'
'''

create_trigger = Clock.create_trigger


@types.coroutine
def sleep_original(duration):
    args, kwargs = yield lambda step_coro: create_trigger(step_coro, duration, release_ref=False)()
    return args[0]


@types.coroutine
def sleep_new1(duration):
    '''removed CALL_FUNCTION_KW'''
    args, kwargs = yield lambda step_coro: create_trigger(step_coro, duration, False, False)()
    return args[0]


@types.coroutine
def sleep_new2(duration):
    '''removed closure'''
    args, kwargs = yield lambda step_coro, _d=duration: create_trigger(step_coro, _d, False, False)()
    return args[0]


def print_byte_code():
    from dis import dis
    for key, obj in globals().items():
        if not key.startswith("sleep_"):
            continue
        print("---- byte code ----", key)
        dis(obj)
        print("\n\n")


print_byte_code()


async def repeat_sleep(sleep):
    while True:
        await sleep(0)


class SampleApp(App):
    def build(self):
        self._tasks = []
        return Builder.load_string(KV_CODE)

    def on_start(self):
        def print_fps(dt):
            print(Clock.get_fps(), 'fps')
        Clock.schedule_interval(print_fps, 1)

    def measure_fps(self, type):
        print('---- start measuring ----', type)
        sleep = globals()['sleep_' + type]
        for task in self._tasks:
            task.cancel()
        self._tasks = [ak.start(repeat_sleep(sleep)) for __ in range(10)]


if __name__ == '__main__':
    SampleApp().run()
