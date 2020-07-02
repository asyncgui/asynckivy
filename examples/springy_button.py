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
            rgba: self.background_color
        Rectangle:
            pos: self.x + dp(4), self.y + dp(4)
            size: self.width - dp(8), self.height - dp(8)
        PopMatrix:
'''
Builder.load_string(KV_CODE)


class SpringyButton(Label):
    __events__ = ('on_press', 'on_release', )
    border_color1 = ColorProperty('#666666')
    border_color2 = ColorProperty('#AAAA33')
    background_color = ColorProperty('#999933')
    _border_color = ColorProperty('#666666')
    _scaling = NumericProperty(1)
    _ctx = None

    def on_press(self):
        pass

    def on_release(self):
        pass

    def on_border_color1(self, __, color1):
        if self._ctx is None:
            self._border_color = color1

    def on_touch_down(self, touch):
        if self._ctx is None and self.collide_point(*touch.opos) \
                and not touch.is_mouse_scrolling:
            ak.start(self._handle_touch(touch))
            return True
        return super().on_touch_down(touch)

    async def _handle_touch(self, touch):
        from asynckivy import animate, Event, rest_of_touch_moves, start
        self._ctx = True
        self.dispatch('on_press')
        try:
            flag_proceed_blinking = Event()
            flag_proceed_blinking.set()
            coro_blink = start(self._blink(flag_proceed_blinking))
            async for __ in rest_of_touch_moves(self, touch):
                if self.collide_point(*touch.pos):
                    flag_proceed_blinking.set()
                else:
                    flag_proceed_blinking.clear()
            if self.collide_point(*touch.pos):
                await animate(self, _scaling=.9, d=.05)
                await animate(self, _scaling=1, d=.05)
                self.dispatch('on_release')
        finally:
            coro_blink.close()
            self._ctx = None

    async def _blink(self, flag_proceed):
        try:
            color1 = self.border_color1
            color2 = self.border_color2
            sleep = await ak.create_sleep(.1)
            while True:
                await flag_proceed.wait()
                self._border_color = color2
                await sleep()
                self._border_color = color1
                await sleep()
        finally:
            self._border_color = color1


from kivy.app import App
from kivy.lang import Builder


KV_CODE = '''
BoxLayout:
    padding: 40
    spacing: 40
    SpringyButton:
        text: 'Hello'
        border_color1: 0, 0, .6, 1
        border_color2: .3, .4, 1, 1
        background_color: .6, .3, .6, 1
        on_press: print('blue: on_press')
        on_release: print('blue: on_release')
    RelativeLayout:
        SpringyButton:
            text: 'Kivy'
            size_hint: .8, .3
            pos_hint: {'center_x': .5, 'center_y': .7, }
            on_press: print('orange: on_press')
            on_release: print('orange: on_release')
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
