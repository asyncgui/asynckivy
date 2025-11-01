from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from kivy.core.window import Window, WindowBase
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout


import asynckivy as ak
from asynckivy import modal


Builder.load_string('''
<ProgressDialog@BoxLayout>:
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
        id: label
        size_hint_min: self.texture_size
    Widget:
        id: bar
        canvas:
            Color:
                rgb: .5, .5, .8
            Rectangle:
                size: self.width * root.progress, self.height
                pos: self.pos
            Color:
            Line:
                width: dp(2)
                rectangle: (*self.pos, *self.size, )
    Button:
        id: cancel_button
        size_hint_x: .3
        size_hint_min: self.texture_size
        pos_hint: {'center_x': .5}
        text: "Cancel"
''')


class ProgressDialog(BoxLayout):
    progress = NumericProperty()
    '''
    The current progress value.
    Setting this value will instantly change the progress bar to the corresponding length.
    '''

    goal_progress = NumericProperty()
    '''
    Setting this value will make :attr:`progress` smoothly follow it.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ak.smooth_attr((self, 'goal_progress'), (self, 'progress'), min_diff=0.01)
        self.cancelled = False
        '''Whether the user dismissed the dialog via its cancel button.'''


@asynccontextmanager
async def open_progress_dialog(
    text: str, *, progress=0.,
    window: WindowBase=Window, transition=modal.SlideTransition(), _cache=[],
) -> AsyncIterator[ProgressDialog]:
    '''
    .. code-block::

        async with open_progress_dialog("Loading...") as dialog:
            ...
    '''
    dialog = _cache.pop() if _cache else ProgressDialog()
    try:
        dialog.cancelled = False
        dialog.goal_progress = dialog.progress = progress
        dialog.ids.label.text = text
        async with (
            modal.open(dialog, window=window, auto_dismiss=False, transition=transition),
            ak.move_on_when(ak.event(dialog.ids.cancel_button, 'on_release')) as cancel_tracker,
        ):
            yield dialog
    finally:
        dialog.cancelled = cancel_tracker.finished
        _cache.append(dialog)


def main():
    from textwrap import dedent
    import requests
    from kivy.lang import Builder
    from kivy.app import App

    class TestApp(App):
        def build(self):
            return Builder.load_string(dedent('''
                #:import ak asynckivy

                <Label>:
                    font_size: '24sp'

                AnchorLayout:
                    Button:
                        id: button
                        size_hint: .4, .2
                        size_hint_min: self.texture_size
                        padding: '10dp'
                        text: "open dialog"
                        on_release: ak.managed_start(app.demonstrate_progress_dialog())
                '''))

        async def demonstrate_progress_dialog(self):
            from functools import partial
            from asynckivy import transition
            from message_box import show_message_box

            async with open_progress_dialog("Preparing...") as dialog:
                label = dialog.ids.label
                ft = partial(transition.fade, label, duration=.3)
                await ak.sleep(1)

                async with ft():
                    label.text = "Sleeping..."
                dialog.goal_progress = 0.3
                await ak.sleep(2)

                async with ft():
                    label.text = "Downloading..."
                dialog.goal_progress = 0.8
                res = await ak.run_in_thread(lambda: requests.get("https://httpbin.org/delay/1"))

                async with ft():
                    label.text = res.json()['headers']['User-Agent']
                await ak.sleep(1)

                async with ft():
                    label.text = "Time is flowing backward"
                await ak.anim_attrs(dialog, progress=.1)

                async with ft():
                    label.text = "Just kidding"
                dialog.goal_progress = 1.0
                await ak.sleep(1.5)
            if dialog.cancelled:
                await show_message_box("Operation was cancelled.")
    TestApp().run()


if __name__ == '__main__':
    main()
