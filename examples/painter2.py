'''
Painter
=======

* can only handle one touch at a time
'''

from functools import partial
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App
from kivy.graphics import Line, Color
from kivy.utils import get_random_color
import asynckivy as ak


class Painter(RelativeLayout):
    @staticmethod
    def accepts_touch(widget, touch) -> bool:
        return widget.collide_point(*touch.opos) and (not touch.is_mouse_scrolling)

    async def main(self):
        on_touch_down = partial(ak.event, self, 'on_touch_down', filter=self.accepts_touch, stop_dispatching=True)
        while True:
            __, touch = await on_touch_down()
            await self.draw_rect(touch)

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
        ak.managed_start(self.root.main())


if __name__ == "__main__":
    SampleApp(title='Painter').run()
