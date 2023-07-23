'''
Painter
=======

* can handle multiple touches simultaneously
'''

from functools import cached_property
from kivy.graphics import Line, Color
from kivy.utils import get_random_color
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import runTouchApp
import asynckivy as ak


class Painter(RelativeLayout):
    @cached_property
    def _ud_key(self):
        return 'Painter.' + str(self.uid)

    def will_accept_touch(self, touch) -> bool:
        return self.collide_point(*touch.opos) and (not touch.is_mouse_scrolling) and (self._ud_key not in touch.ud)

    def on_touch_down(self, touch):
        if self.will_accept_touch(touch):
            touch.ud[self._ud_key] = True
            ak.start(self.draw_rect(touch))
            return True

    async def draw_rect(self, touch):
        with self.canvas:
            Color(*get_random_color())
            line = Line(width=2)
        self_to_local = self.to_local
        ox, oy = self_to_local(*touch.opos)
        async for __ in ak.rest_of_touch_events(self, touch, stop_dispatching=True):
            # Don't await anything during the iteration
            x, y = self_to_local(*touch.pos)
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            line.rectangle = (min_x, min_y, max_x - min_x, max_y - min_y, )


if __name__ == "__main__":
    runTouchApp(Painter())
