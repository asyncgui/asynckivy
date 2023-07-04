from functools import partial
from kivy.config import Config
Config.set('graphics', 'maxfps', 0)
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
from asyncgui import IBox, ISignal, Cancelled
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
        text: 'box'
    MyToggleButton:
        text: 'box2'
    MyToggleButton:
        text: 'signal'
    MyToggleButton:
        text: 'ugly1'
    MyToggleButton:
        text: 'ugly2'
    MyToggleButton:
        text: 'ugly3'
    MyToggleButton:
        text: 'closure'
'''

create_trigger = Clock.create_trigger


async def sleep_ver_box(duration):
    box = IBox()
    create_trigger(box.put, duration, False, False)()
    return (await box.get())[0][0]


async def sleep_ver_box2(duration):
    box = IBox()
    create_trigger(box.put, duration, False, False)()
    args, kwargs = await box.get()
    return args[0]


async def sleep_ver_signal(duration):
    signal = ISignal()
    create_trigger(signal.set, duration, False, False)()
    await signal.wait()


def _func1(ctx, duration, task):
    ctx['ce'] = ce = create_trigger(task._step, duration, False, False)
    ce()


def _func2(ctx, duration, task):
    ctx[0] = ce = create_trigger(task._step, duration, False, False)
    ce()


def _func3(ctx, duration, task):
    ctx.data = ce = create_trigger(task._step, duration, False, False)
    ce()


class DataPassenger:
    __slots__ = ('data', )


@types.coroutine
def sleep_ver_ugly1(duration):
    ctx = {}
    try:
        return (yield partial(_func1, ctx, duration))[0][0]
    except Cancelled:
        ctx['ce'].cancel()
        raise


@types.coroutine
def sleep_ver_ugly2(duration):
    ctx = [None, ]
    try:
        return (yield partial(_func2, ctx, duration))[0][0]
    except Cancelled:
        ctx[0].cancel()
        raise


@types.coroutine
def sleep_ver_ugly3(duration):
    ctx = DataPassenger()
    try:
        return (yield partial(_func3, ctx, duration))[0][0]
    except Cancelled:
        ctx.data.cancel()
        raise


@types.coroutine
def sleep_ver_closure(duration):
    clock_event = None

    def _inner(task):
        nonlocal clock_event
        clock_event = create_trigger(task._step, duration, False, False)
        clock_event()

    try:
        return (yield _inner)[0][0]
    except Cancelled:
        clock_event.cancel()
        raise


def print_byte_code():
    from dis import dis
    for key, obj in globals().items():
        if not key.startswith("sleep_ver_"):
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
        sleep = globals()['sleep_ver_' + type]
        for task in self._tasks:
            task.cancel()
        self._tasks = [ak.start(repeat_sleep(sleep)) for __ in range(10)]


if __name__ == '__main__':
    SampleApp().run()
