from kivy.properties import ColorProperty, NumericProperty
from kivy.lang import Builder
from kivy.uix.label import Label


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
        import asynckivy
        super().__init__(**kwargs)
        asynckivy.start(self.main())

    def on_press(self):
        pass

    def on_release(self):
        pass

    async def main(self):
        import asynckivy
        from asynckivy import animation, or_, event

        while True:
            __, current_touch = await event(
                self, 'on_touch_down',
                filter=lambda w, t: w.collide_point(*t.opos) and not t.is_mouse_scrolling,
                return_value=True,
            )
            self.dispatch('on_press')
            current_touch.grab(self)
            coro_blink = self._blink()
            asynckivy.start(coro_blink)
            await event(self, 'on_touch_up',
                filter=lambda w, t: t is current_touch and t.grab_current is w,
                return_value=True,
            )
            coro_blink.close()
            current_touch.ungrab(self)
            if self.collide_point(*current_touch.pos):
                self.dispatch('on_release')
                await animation(self, _scaling=.9, d=.05)
                await animation(self, _scaling=1, d=.05)

    async def _blink(self):
        from asynckivy import animation
        try:
            previous_color = self._border_color
            while True:
                await animation(
                    self, d=.1,
                    _border_color=(.7, .7, .2, 1),
                )
                await animation(
                    self, d=.1,
                    _border_color=previous_color,
                )
        finally:
            self._border_color = previous_color



from kivy.app import App
from kivy.lang import Builder


KV_CODE = '''
BoxLayout:
    padding: 20
    spacing: 20
    SpringyButton:
        text: 'Hello'
        on_press: print('Hello')
    RelativeLayout:
        SpringyButton:
            text: 'Kivy'
            on_release: print('Kivy')
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
