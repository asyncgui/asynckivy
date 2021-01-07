from kivy.app import runTouchApp
from kivy.lang.builder import Builder
import asynckivy

KV_CODE = '''
BoxLayout:
    Widget:
    RelativeLayout:
        Widget:
            id: target
'''


async def test_gui_event(widget):
    event = asynckivy.event
    while True:
        __, touch = await event(widget, 'on_touch_down')
        print(touch.uid, 'down', touch.opos)
        __, touch = await event(widget, 'on_touch_up')
        print(touch.uid, 'up  ', touch.pos)


def _test():
    root = Builder.load_string(KV_CODE)
    asynckivy.start(test_gui_event(root.ids.target))
    runTouchApp(root)


if __name__ == '__main__':
    _test()
