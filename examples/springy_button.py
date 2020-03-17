from kivy.properties import ColorProperty, NumericProperty
from kivy.lang import Builder
from kivy.uix.label import Label

import asynckivy

KV_CODE = '''
<SpringyButton>:
    outline_width: 4
    outline_color: 0, 0, 0, 1
    font_size: 30
    canvas.before:
        PushMatrix:
        Scale:
            origin: self.center
            x: self._scaling
            y: self._scaling
        Color:
            rgba: self._border_color
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: self._background_color
        Rectangle:
            pos: self.x + dp(4), self.y + dp(4)
            size: self.width - dp(8), self.height - dp(8)
        PopMatrix:
'''
Builder.load_string(KV_CODE)


class SpringyButton(Label):
    __events__ = ('on_press', 'on_release', )
    _border_color = ColorProperty('#666666')
    _scaling = NumericProperty(1)
    _background_color = ColorProperty('#999933')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._coro_blink = None
        asynckivy.start(self.main())

    def on_press(self):
        pass

    def on_release(self):
        pass

    def start_blinking(self):
        if self._coro_blink is None:
            self._coro_blink = self._blink()
            asynckivy.start(self._coro_blink)

    def stop_blinking(self):
        if self._coro_blink is not None:
            self._coro_blink.close()
            self._coro_blink = None

    async def main(self):
        from asynckivy import animate, event, rest_of_touch_moves

        try:
            while True:
                __, touch = await event(
                    self, 'on_touch_down',
                    filter=lambda w, t: w.collide_point(*t.opos) and not t.is_mouse_scrolling,
                    return_value=True,
                )
                self.dispatch('on_press')
                self.start_blinking()
                async for __ in rest_of_touch_moves(self, touch):
                    if self.collide_point(*touch.pos):
                        self.start_blinking()
                    else:
                        self.stop_blinking()
                if self.collide_point(*touch.pos):
                    self.dispatch('on_release')
                    await animate(self, _scaling=.9, d=.05)
                    await animate(self, _scaling=1, d=.05)
                self.stop_blinking()
        finally:
            self.stop_blinking()

    async def _blink(self):
        from asynckivy import sleep
        try:
            previous_color = self._border_color
            while True:
                self._border_color = (.7, .7, .2, 1)
                await sleep(.1)
                self._border_color = previous_color
                await sleep(.1)
        finally:
            self._border_color = previous_color


from kivy.app import App
from kivy.lang import Builder


KV_CODE = '''
BoxLayout:
    padding: 40
    spacing: 40
    SpringyButton:
        text: 'Hello'
        on_press: print('on_press: Hello')
        on_release: print('on_release: Hello')
    RelativeLayout:
        SpringyButton:
            text: 'Kivy'
            on_press: print('on_press: Kivy')
            on_release: print('on_release: Kivy')
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
