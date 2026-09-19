from textwrap import dedent

from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak


class SampleApp(App):
    def on_start(self):
        ak.managed_start(add_a_confirmation_step_before_quitting_the_app())


async def add_a_confirmation_step_before_quitting_the_app(*, window=None):
    '''
    Prevents the app from quitting immediately when the user presses the Escape key.

    Instead, a message is displayed for 1 second.
    To quit the app, the user must press the Escape key again while the message is displayed.

    * The effect of this function lasts until the returned coroutine is cancelled.
    * Alt+F4 and the window's close button are not affected by this function.
    '''
    if window is None:
        from kivy.core.window import Window
        window = Window

    label = Builder.load_string(dedent("""
        Label:
            text: "Press again to quit the app"
            font_size: "24sp"
            padding: [dp(16), dp(8)]
            size_hint: None, None
            size: self.texture_size
            pos_hint: {"center_x": .5, "y": 0.08}
            canvas.before:
                Color:
                    rgb: 0.2, 0.2, 0.2
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
        """))
    try:
        label.opacity = 0.
        while True:
            await ak.event(window, "on_request_close", stop_dispatching=True)
            window.add_widget(label)
            await ak.anim_attrs(label, opacity=1, duration=.2)
            await ak.sleep(1)
            await ak.anim_attrs(label, opacity=0, duration=.2)
            window.remove_widget(label)
    finally:
        window.remove_widget(label)


if __name__ == "__main__":
    SampleApp(title="Press the Escape key").run()
