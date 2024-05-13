from functools import cached_property

from kivy.properties import NumericProperty
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import asynckivy as ak


class GestureRecognizer:
    __events__ = ('on_gesture_swipe', 'on_gesture_long_press', )

    gesture_distance = NumericProperty(ScrollView.scroll_distance.defaultvalue)
    gesture_timeout = NumericProperty(ScrollView.scroll_timeout.defaultvalue)

    @cached_property
    def _ud_key(self):
        return 'GestureRecognizer.' + str(self.uid)

    def _touch_filter(self, touch) -> bool:
        return self.collide_point(*touch.opos) \
            and (not touch.is_mouse_scrolling) \
            and (self._ud_key not in touch.ud) \
            and (touch.time_end == -1)

    def on_touch_down(self, touch):
        if self._touch_filter(touch):
            touch.ud[self._ud_key] = None
            ak.start(self._track_touch(touch))
            return True
        else:
            touch.ud[self._ud_key] = None
            return super().on_touch_down(touch)

    async def _track_touch(self, touch):
        async with ak.move_on_after(self.gesture_timeout / 1000.) as bg_task:
            # LOAD_FAST
            abs_ = abs
            gesture_distance = self.gesture_distance
            ox, oy = touch.opos

            async with ak.watch_touch(self, touch) as in_progress:
                while await in_progress():
                    dx = abs_(touch.x - ox)
                    dy = abs_(touch.y - oy)
                    if dy > gesture_distance or dx > gesture_distance:
                        self.dispatch('on_gesture_swipe', touch)
                        return

        if bg_task.finished:
            touch.push()
            touch.apply_transform_2d(self.parent.to_widget)
            self.dispatch('on_gesture_long_press', touch)
            touch.pop()
        else:
            await self._simulate_a_normal_touch(touch)

    async def _simulate_a_normal_touch(self, touch):
        # simulates an 'on_touch_down' event
        orig = touch.grab_current
        touch.grab_current = None
        super().on_touch_down(touch)
        touch.grab_current = orig

        await ak.sleep(.1)

        # simulates an 'on_touch_up' event
        to_widget = self.to_widget if self.parent is None else self.parent.to_widget
        touch.grab_current = None
        touch.push()
        touch.apply_transform_2d(to_widget)
        super().on_touch_up(touch)
        touch.pop()

        # simulates an 'on_touch_up' event (grab)
        for x in tuple(touch.grab_list):
            touch.grab_list.remove(x)
            x = x()
            if x is None:
                continue
            touch.grab_current = x
            touch.push()
            touch.apply_transform_2d(x.parent.to_widget)
            x.dispatch('on_touch_up', touch)
            touch.pop()

        touch.grab_current = None
        return

    def on_gesture_swipe(self, touch):
        pass

    def on_gesture_long_press(self, touch):
        pass


class GestureTest(GestureRecognizer, Button):
    def on_gesture_swipe(self, touch):
        self.text = 'swipe'

    def on_gesture_long_press(self, touch):
        self.text = 'long press'

    def on_press(self):
        self.text = ''


class SampleApp(App):
    def build(self):
        return GestureTest(font_size='50sp', outline_width='2sp', outline_color=(0, 0, 0, 1))


if __name__ == "__main__":
    SampleApp(title='Gesture Recognition').run()
