import asyncio
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
    event = asyncio.Event()
    await event.wait()
    return parameter


async def test_gui_event(widget):
    try:
        while True:
            __, touch = await kivy_event(widget, 'on_touch_down')
            print(touch.uid, 'down', touch.opos)
            __, touch = await kivy_event(widget, 'on_touch_up')
            print(touch.uid, 'up  ', touch.pos)
    except asyncio.CancelledError:
        pass


async def async_main():
    root = Builder.load_string(KV_CODE)
    sub_task = asyncio.ensure_future(test_gui_event(root.ids.target))

    async def main_task():
        await async_runTouchApp(root, async_lib='asyncio')
        sub_task.cancel()

    await asyncio.gather(main_task(), sub_task)


if __name__ == '__main__':
    asyncio.run(async_main())
