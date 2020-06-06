from kivy.properties import ColorProperty, NumericProperty
from kivy.lang import Builder
from kivy.uix.label import Label

import asynckivy as ak

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

    def on_kv_post(self, *args, **kwargs):
        ak.start(self._main())

    def on_press(self):
        pass

    def on_release(self):
        pass

    async def _main(self):
        from asynckivy import animate, event, rest_of_touch_moves, start

        coro_blink = None
        def close_coro_blink():
            nonlocal coro_blink
            if coro_blink is None:
                return
            coro_blink.close()
            coro_blink = None
        try:
            while True:
                __, touch = await event(
                    self, 'on_touch_down',
                    filter=lambda w, t: w.collide_point(*t.opos) and not t.is_mouse_scrolling,
                    return_value=True,
                )
                self.dispatch('on_press')
                coro_blink = start(self._blink())
                async for __ in rest_of_touch_moves(self, touch):
                    if self.collide_point(*touch.pos):
                        if coro_blink is None:
                            coro_blink = start(self._blink())
                    else:
                        close_coro_blink()
                if self.collide_point(*touch.pos):
                    self.dispatch('on_release')
                    await animate(self, _scaling=.9, d=.05)
                    await animate(self, _scaling=1, d=.05)
                close_coro_blink()
        finally:
            close_coro_blink()

    async def _blink(self):
        try:
            previous_color = self._border_color
            sleep = await ak.create_sleep(.1)
            while True:
                self._border_color = (.7, .7, .2, 1)
                await sleep()
                self._border_color = previous_color
                await sleep()
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
    RelativeLayout:
        SpringyButton:
            text: 'Kivy'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
