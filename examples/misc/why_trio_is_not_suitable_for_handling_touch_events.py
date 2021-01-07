import trio
import kivy
from kivy.app import async_runTouchApp
from kivy.lang.builder import Builder
kivy.require('2.0.0')


KV_CODE = '''
BoxLayout:
    Widget:
    RelativeLayout:
        Widget:
            id: target
'''


async def kivy_event(ed, name):
    def callback(*args, **kwargs):
        nonlocal parameter
        parameter = args
        ed.unbind_uid(name, bind_uid)
        event.set()

    parameter = None
    bind_uid = ed.fbind(name, callback)
    event = trio.Event()
    await event.wait()
    return parameter


async def test_gui_event(widget):
    while True:
        __, touch = await kivy_event(widget, 'on_touch_down')
        print(touch.uid, 'down', touch.opos)
        __, touch = await kivy_event(widget, 'on_touch_up')
        print(touch.uid, 'up  ', touch.pos)


async def root_task():
    root = Builder.load_string(KV_CODE)
    async with trio.open_nursery() as nursery:
        async def main_task():
            await async_runTouchApp(root, async_lib='trio')
            nursery.cancel_scope.cancel()
        nursery.start_soon(test_gui_event, root.ids.target)
        nursery.start_soon(main_task)


if __name__ == '__main__':
    trio.run(root_task)
