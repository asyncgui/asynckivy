'''
Painter
=======

* can handle mutiple touches simultaneously
'''

from functools import cached_property, partial
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App
import asynckivy as ak
from kivy.graphics import Line, Color
from kivy.utils import get_random_color


class Painter(RelativeLayout):
    @cached_property
    def _ud_key(self):
        return 'Painter.' + str(self.uid)

    @staticmethod
    def accepts_touch(self, touch) -> bool:
        return self.collide_point(*touch.opos) and (not touch.is_mouse_scrolling) and (self._ud_key not in touch.ud)

    async def main(self):
        async with ak.open_nursery() as nursery:
            touch_down_event = partial(
                ak.event, self, 'on_touch_down', filter=self.accepts_touch, stop_dispatching=True)

            while True:
                __, touch = await touch_down_event()
                touch.ud[self._ud_key] = True
                nursery.start(self.draw_rect(touch))

    async def draw_rect(self, touch):
        # LOAD_FAST
        self_to_local = self.to_local
        ox, oy = self_to_local(*touch.opos)

        with self.canvas:
            Color(*get_random_color())
            line = Line(width=2)

        async for __ in ak.rest_of_touch_events(self, touch, stop_dispatching=True):
            # Don't await anything during the loop
            x, y = self_to_local(*touch.pos)
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            line.rectangle = (min_x, min_y, max_x - min_x, max_y - min_y, )


class SampleApp(App):
    def build(self):
        return Painter()

    def on_start(self):
        ak.start(self.root.main())


if __name__ == "__main__":
    SampleApp(title='Painter').run()
