'''
Painter
=======

* can only draw rectangles
* can handle multiple touches simultaneously
'''

from kivy.utils import reify
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import runTouchApp
import asynckivy as ak


class Painter(RelativeLayout):
    @reify
    def _ud_key(self):
        return 'Painter.' + str(self.uid)

    def will_accept_touch(self, touch) -> bool:
        return self.collide_point(*touch.opos) and \
            (not touch.is_mouse_scrolling) and \
            (self._ud_key not in touch.ud)

    def on_touch_down(self, touch):
        if self.will_accept_touch(touch):
            touch.ud[self._ud_key] = True
            ak.start(self.draw_rect(touch))
            return True

    async def draw_rect(self, touch):
        from kivy.graphics import Line, Color, Rectangle, InstructionGroup
        from kivy.utils import get_random_color
        inst_group = InstructionGroup()
        self.canvas.add(inst_group)
        inst_group.add(Color(*get_random_color()))
        line = Line(width=2)
        inst_group.add(line)
        ox, oy = x, y = self.to_local(*touch.opos)
        async for __ in ak.rest_of_touch_moves(
                self, touch, stop_dispatching=True):
            # Don't await anything during the iteration
            x, y = self.to_local(*touch.pos)
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            line.rectangle = (min_x, min_y, max_x - min_x, max_y - min_y, )
        if x == ox and y == oy:
            self.canvas.remove(inst_group)
        else:
            inst_group.add(Color(*get_random_color(alpha=.3)))
            inst_group.add(
                Rectangle(
                    pos=(min_x, min_y),
                    size=(max_x - min_x, max_y - min_y, ),
                )
            )


if __name__ == "__main__":
    runTouchApp(Painter())
