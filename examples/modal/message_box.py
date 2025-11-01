from typing import Literal
from collections.abc import Awaitable

from kivy.core.window import Window, WindowBase
from kivy.lang import Builder
from kivy.factory import Factory


import asynckivy as ak
from asynckivy import modal


Builder.load_string('''
<MessageBox@BoxLayout>:
    padding: '20dp'
    spacing: '20dp'
    orientation: 'vertical'
    size_hint: .5, .5
    size_hint_min: self.minimum_size
    pos_hint: {'center_x': .5, 'center_y': .5}
    canvas.before:
        Color:
        Line:
            width: dp(2)
            rectangle: (*self.pos, *self.size, )
    Label:
        id: msg
        size_hint_min: self.texture_size
    Button:
        id: ok_button
        size_hint: .3, .5
        size_hint_min: self.texture_size
        pos_hint: {'center_x': .5}
''')
MessageBox = Factory.MessageBox


async def show_message_box(
    message: str, *, window: WindowBase=Window, ok_text='OK',
    transition=modal.SlideTransition(), auto_dismiss=True, _cache=[],
) -> Awaitable[Literal[True, None]]:
    '''
    .. code-block::

        answer = await show_message_box("Learn Kivy!")

    :return: True if the "OK" button is pressed. None if the dialog is auto-dismissed.
    '''
    dialog = _cache.pop() if _cache else MessageBox()
    try:
        ids = dialog.ids
        ids.msg.text = message
        ids.ok_button.text = ok_text
        async with modal.open(dialog, window=window, auto_dismiss=auto_dismiss, transition=transition) as ad_event:
            await ak.event(ids.ok_button, 'on_release')
        if ad_event.is_fired:
            return None
        return True
    finally:
        _cache.append(dialog)


def main():
    from textwrap import dedent
    from kivy.lang import Builder
    from kivy.app import App

    class TestApp(App):
        def build(self):
            return Builder.load_string(dedent('''
                #:import ak asynckivy
                #:import show_message_box __main__.show_message_box

                <Label>:
                    font_size: '24sp'

                AnchorLayout:
                    Button:
                        id: button
                        size_hint: .4, .2
                        size_hint_min: self.texture_size
                        text: "open dialog"
                        on_release:
                            ak.managed_start(show_message_box(
                            "The armor I used to seal my all too powerful strength is now broken."))
                '''))
    TestApp().run()


if __name__ == '__main__':
    main()
