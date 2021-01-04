'''
Springy Button
==============

* can only handle one touch at a time
'''

from kivy.properties import ColorProperty, NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.app import App


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

    def on_press(self):
        pass

    def on_release(self):
        pass

    def on_kv_post(self, *args, **kwargs):
        import asynckivy
        asynckivy.start(self._async_main())

    async def _async_main(self):
        from asynckivy import animate, rest_of_touch_moves, event

        def will_accept_touch(w, t) -> bool:
            return w.collide_point(*t.opos) and (not t.is_mouse_scrolling)

        # 'itertools.cycle()' is no use here because it cannot react to
        # the property changes. There might be a better way, though.
        def color_iter(w):
            while True:
                yield w.border_color2
                yield w.border_color1
        color_iter = color_iter(self)

        def change_border_color(dt):
            self._border_color = next(color_iter)
        blink_ev = Clock.create_trigger(change_border_color, .1, interval=True)

        while True:
            __, touch = await event(
                self, 'on_touch_down', filter=will_accept_touch,
                return_value=True)
            self.dispatch('on_press')
            blink_ev()
            async for __ in rest_of_touch_moves(self, touch):
                if self.collide_point(*touch.pos):
                    blink_ev()
                else:
                    blink_ev.cancel()
                    self._border_color = self.border_color1
            if self.collide_point(*touch.pos):
                await animate(self, _scaling=.9, d=.05)
                await animate(self, _scaling=1, d=.05)
                self.dispatch('on_release')
            blink_ev.cancel()
            self._border_color = self.border_color1


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
