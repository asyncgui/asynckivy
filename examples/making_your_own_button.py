import itertools
from functools import partial
from kivy.properties import ColorProperty, NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics import Scale
from kivy.uix.label import Label
from kivy.app import App

import asynckivy as ak


KV_CODE = '''
<CustomButton>:
    canvas.before:
        Color:
            rgba: self._border_color
        Line:
            width: self.border_width
            joint: 'miter'
            rectangle:
                (bw := self.border_width, ) and (*self.pos, self.width - bw, self.height - bw, )
'''
Builder.load_string(KV_CODE)


class CustomButton(Label):
    __events__ = ('on_press', 'on_release', 'on_cancel', )

    border_color1 = ColorProperty('#666666')
    border_color2 = ColorProperty('#AAAA33')
    border_width = NumericProperty('4dp')
    border_blinking_interval = NumericProperty(.1)

    _border_color = ColorProperty(border_color1.defaultvalue)
    _props_that_trigger_to_restart = (
        'disabled', 'parent', 'border_color1', 'border_color2', 'border_blinking_interval',
    )

    def on_press(self):
        pass

    def on_release(self, finger_is_inside: bool):
        pass

    def on_cancel(self):
        '''This event occurs when any of '_props_that_trigger_to_restart' changes in the middle of a touch.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._main_task = ak.dummy_task
        fbind = self.fbind
        trigger = Clock.schedule_once(self._restart)
        for prop in self._props_that_trigger_to_restart:
            fbind(prop, trigger)

    def _restart(self, dt):
        self._main_task.cancel()
        self._main_task = ak.start(self._main())

    @staticmethod
    def _touch_filter(w, t) -> bool:
        return w.collide_point(*t.opos) and (not t.is_mouse_scrolling)

    @staticmethod
    def _blink_border(self, next_color, dt):
        self._border_color = next_color()

    async def _main(self):
        import asynckivy as ak

        if self.parent is None or self.disabled:
            self._border_color = self.disabled_color
            return

        self._border_color = self.border_color1
        blink_trigger = Clock.create_trigger(
            partial(self._blink_border, self, itertools.cycle((self.border_color2, self.border_color1, )).__next__),
            self.border_blinking_interval, interval=True,
        )

        # LOAD_FAST
        blink_trigger_cancel = blink_trigger.cancel
        collide_point = self.collide_point
        abs_ = abs
        try:
            while True:
                __, touch = await ak.event(self, 'on_touch_down', filter=self._touch_filter, stop_dispatching=True)
                self.dispatch('on_press')
                blink_trigger()
                try:
                    async for __ in ak.rest_of_touch_events(self, touch, stop_dispatching=True):
                        if collide_point(*touch.pos):
                            blink_trigger()
                        else:
                            blink_trigger_cancel()
                            self._border_color = self.border_color1
                except ak.Cancelled:
                    self.dispatch('on_cancel')
                    raise
                except ak.MotionEventAlreadyEndedError:
                    blink_trigger_cancel()
                    self._border_color = self.border_color1
                    continue
                inside = collide_point(*touch.pos)
                if inside:
                    async with ak.disable_cancellation():
                        with ak.transform(self, use_outer_canvas=True) as group:
                            group.add(scale := Scale(origin=self.center))
                            async for v in ak.interpolate(start=-0.1, end=0.1, duration=0.1):
                                scale.x = scale.y = abs_(v) + 0.9
                self.dispatch('on_release', inside)
                blink_trigger_cancel()
                self._border_color = self.border_color1
        finally:
            blink_trigger_cancel()
            self._border_color = self.border_color1


KV_CODE = '''
BoxLayout:
    padding: 40, 100
    spacing: 40
    CustomButton:
        font_size: 30
        text: 'Hello'
        disabled: not switch.active
        border_color1: 0, 0, .6, 1
        border_color2: .3, .4, 1, 1
        on_release: print(f"The {self.text!r} button released. (inside = {args[1]})")
        on_cancel: print(f"The {self.text!r} button cancelled.")
    CustomButton:
        font_size: 30
        text: 'Kivy'
        disabled: not switch.active
        border_color1: .3, .3, 0, 1
        border_blinking_interval: 0.05
        on_release: print(f"The {self.text!r} button released. (inside = {args[1]})")
        on_cancel: print(f"The {self.text!r} button cancelled.")
    Switch:
        id: switch
        active: True
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp(title='build your own button').run()
