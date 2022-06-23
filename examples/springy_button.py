'''
Springy Button
==============

Notable differences from the official Button
--------------------------------------------

* can only handle one touch at a time
'''
import itertools
from functools import partial
# from kivy.config import Config
# Config.set('modules', 'showborder', '')
from kivy.properties import ColorProperty, NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.app import App

import asynckivy


KV_CODE = '''
<-SpringyButton>:
    canvas:
        PushMatrix:
        Translate:
            xy: self.center
        Scale:
            x: self._scaling
            y: self._scaling
        Color:
            rgba: self._border_color
        Line:
            width: self.border_width
            joint: 'miter'
            rectangle:
                (
                bw := self.border_width,
                hw := self.width / 2. - bw,
                hh := self.height / 2. - bw,
                ) and (-hw, -hh, 2 * hw, 2 * hh, )

        # Since this widget doesn't inherit the Label's kv rules, we need to re-write them.
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: self.texture_size[0] / -2., self.texture_size[1] / -2.

        PopMatrix:
'''
Builder.load_string(KV_CODE)


class SpringyButton(Label):
    __events__ = ('on_press', 'on_release', )
    border_color1 = ColorProperty('#666666')
    border_color2 = ColorProperty('#AAAA33')
    border_width = NumericProperty('4dp')
    border_blinking_interval = NumericProperty(.1)
    _border_color = ColorProperty(border_color1.defaultvalue)
    _scaling = NumericProperty(1.)
    _props_that_trigger_to_restart = (
        'disabled', 'parent', 'border_color1', 'border_color2', 'border_blinking_interval',
    )

    def on_press(self):
        pass

    def on_release(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._main_task = asynckivy.dummy_task
        fbind = self.fbind
        trigger = Clock.schedule_once(self._restart)
        for prop in self._props_that_trigger_to_restart:
            fbind(prop, trigger)

    def _restart(self, dt):
        self._main_task.cancel()
        self._main_task = asynckivy.start(self._main())

    @staticmethod
    def _touch_filter(w, t) -> bool:
        return w.collide_point(*t.opos) and (not t.is_mouse_scrolling)

    @staticmethod
    def _blink_border(next_, self, color_iter, dt):
        self._border_color = next_(color_iter)

    async def _main(self):
        from asynckivy import animate, rest_of_touch_moves, event, MotionEventAlreadyEndedError, cancel_protection
        if self.parent is None or self.disabled:
            self._border_color = self.disabled_color
            return

        border_color1 = self.border_color1
        self._border_color = border_color1
        blink_trigger = Clock.create_trigger(
            partial(self._blink_border, next, self, itertools.cycle((self.border_color2, border_color1, ))),
            self.border_blinking_interval, interval=True,
        )
        blink_trigger_cancel = blink_trigger.cancel
        touch_filter = self._touch_filter
        collide_point = self.collide_point
        dispatch = self.dispatch
        try:
            while True:
                __, touch = await event(self, 'on_touch_down', filter=touch_filter, stop_dispatching=True)
                dispatch('on_press')
                blink_trigger()
                try:
                    async for __ in rest_of_touch_moves(self, touch, stop_dispatching=True):
                        if collide_point(*touch.pos):
                            blink_trigger()
                        else:
                            blink_trigger_cancel()
                            self._border_color = border_color1
                except MotionEventAlreadyEndedError:
                    blink_trigger_cancel()
                    self._border_color = border_color1
                    continue
                if collide_point(*touch.pos):
                    async with cancel_protection():
                        await animate(self, _scaling=.9, d=.05)
                        await animate(self, _scaling=1, d=.05)
                    dispatch('on_release')
                blink_trigger_cancel()
                self._border_color = border_color1
        finally:
            blink_trigger_cancel()
            # border_color1 の変化によりtaskが中断される状況を考えるとここではlocal変数のborder_color1は使えない。
            self._border_color = self.border_color1


KV_CODE = '''
BoxLayout:
    padding: 40
    spacing: 40
    SpringyButton:
        font_size: 30
        text: 'Hello'
        disabled: not switch.active
        border_color1: 0, 0, .6, 1
        border_color2: .3, .4, 1, 1
    FloatLayout:
        SpringyButton:
            font_size: 30
            text: 'Kivy'
            disabled: not switch.active
            border_color1: .3, .3, 0, 1
            border_blinking_interval: 0.05
            size_hint: .8, .3
            pos_hint: {'center_x': .5, 'center_y': .7, }
        Switch:
            id: switch
            active: True
            size_hint: None, None
            size: 100, 40
            pos_hint: {'center_x': .6, 'center_y': .1, }
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
