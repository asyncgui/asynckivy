'''
Painter
=======

* can handle multiple touches simultaneously
* uses 'event_freq' and 'move_on_when' instead of 'rest_of_touch_events'
'''

from functools import cached_property, partial
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App
import asynckivy as ak
from kivy.graphics import Line, Color
from kivy.utils import get_random_color
from kivy.core.window import Window


class Painter(RelativeLayout):
    @cached_property
    def _ud_key(self):
        return 'Painter.' + str(self.uid)

    @staticmethod
    def accepts_touch(self, touch) -> bool:
        return self.collide_point(*touch.opos) and (not touch.is_mouse_scrolling) and (self._ud_key not in touch.ud)

    async def main(self):
        on_touch_down = partial(ak.event, self, 'on_touch_down', filter=self.accepts_touch, stop_dispatching=True)
        async with ak.open_nursery() as nursery:
            while True:
                __, touch = await on_touch_down()
                touch.ud[self._ud_key] = True
                nursery.start(self.draw_rect(touch))

    async def draw_rect(self, touch):
        # LOAD_FAST
        self_to_local = self.to_local
        ox, oy = self_to_local(*touch.opos)

        with self.canvas:
            Color(*get_random_color())
            line = Line(width=2)

        def filter(w, t, touch=touch):
            return t is touch
        async with (
            ak.move_on_when(ak.event(Window, 'on_touch_up', filter=filter)),
            ak.event_freq(self, 'on_touch_move', filter=filter, stop_dispatching=True) as on_touch_move,
        ):
            while True:
                await on_touch_move()
                x, y = self_to_local(*touch.pos)
                min_x, max_x = (x, ox) if x < ox else (ox, x)
                min_y, max_y = (y, oy) if y < oy else (oy, y)
                line.rectangle = (min_x, min_y, max_x - min_x, max_y - min_y, )


class SampleApp(App):
    def build(self):
        return Painter()

    def on_start(self):
        ak.managed_start(self.root.main())


if __name__ == "__main__":
    SampleApp(title='Painter').run()
