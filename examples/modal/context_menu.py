from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
from kivy.core.window import Window, WindowBase
from kivy.lang import Builder
from kivy.factory import Factory

import asynckivy as ak
from asynckivy import modal


Builder.load_string('''
<MenuItem@ButtonBehavior+Label>:
    padding: '10dp'
    font_size: '20sp'
    size_hint_min: self.texture_size

<ContextMenu@BoxLayout>:
    orientation: 'vertical'
    size_hint: None, None
    size: self.minimum_size
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.65
        BoxShadow:
            pos: self.pos
            size: self.size
            blur_radius: 32
            spread_radius: -8, -8
            border_radius: 10, 10, 10, 10
        Color:
            rgb: 0.05, 0.05, 0.05
        Rectangle:
            pos: self.pos
            size: self.size
    MenuItem:
        text: 'Cut'
    MenuItem:
        text: 'Copy'
    MenuItem:
        text: 'Paste'
''')
ContextMenu = Factory.ContextMenu


async def show_context_menu_at(pos, *, window: WindowBase=Window, _cache=[]):
    '''
    Opens a context menu at the given position, and waits for the user to select an item.

    :param pos: Top-left corner position of the context menu.
    :return: The text of the selected menu item, or None if auto-dismissed.
    '''
    menu = _cache.pop() if _cache else ContextMenu()
    try:
        await ak.sleep(0)  # Wait for the size of the menu to be calculated
        menu.x = pos[0]
        menu.top = pos[1]
        async with modal.open(menu, window=window, transition=modal.no_transition) as ad_event:
            tasks = await ak.wait_any(*[ak.event(c, 'on_press') for c in menu.children])
        if ad_event.is_fired:
            return None
        for t in tasks:
            if t.finished:
                return t.result[0].text
    finally:
        _cache.append(menu)


def main():
    from textwrap import dedent
    from functools import partial
    from kivy.lang import Builder
    from kivy.app import App

    class TestApp(App):
        def build(self):
            return Builder.load_string(dedent('''
                FloatLayout:
                    Label:
                        text: "Right-click anywhere to open a context menu."
                '''))

        def on_start(self):
            ak.managed_start(self.menu_handler())

        async def menu_handler(self):
            on_right_click = partial(ak.event, self.root, 'on_touch_down', filter=lambda w, t: t.button == 'right')
            while True:
                __, t = await on_right_click()
                selection = await show_context_menu_at(t.pos)
                if selection is not None:
                    print('Selected menu item:', selection)
    TestApp().run()


if __name__ == '__main__':
    main()
