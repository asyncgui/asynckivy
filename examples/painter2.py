'''
Painter
=======

* can only draw rectangles
* can only handle one touch at a time
'''

from kivy.uix.relativelayout import RelativeLayout
from kivy.app import runTouchApp


class Painter(RelativeLayout):
    def on_kv_post(self, *args, **kwargs):
        import asynckivy
        super().on_kv_post(*args, **kwargs)
        asynckivy.start(self.main())

    @staticmethod
    def will_accept_touch(widget, touch) -> bool:
        return widget.collide_point(*touch.opos) and (not touch.is_mouse_scrolling)

    async def main(self):
        from asynckivy import rest_of_touch_moves, event
        from kivy.graphics import Line, Color, Rectangle, InstructionGroup
        from kivy.utils import get_random_color

        will_accept_touch = self.will_accept_touch
        self_to_local = self.to_local
        while True:
            __, touch = await event(self, 'on_touch_down', filter=will_accept_touch, stop_dispatching=True)
            inst_group = InstructionGroup()
            self.canvas.add(inst_group)
            inst_group.add(Color(*get_random_color()))
            line = Line(width=2)
            inst_group.add(line)
            ox, oy = x, y = self_to_local(*touch.opos)
            async for __ in rest_of_touch_moves(self, touch, stop_dispatching=True):
                # Don't await anything during the iteration
                x, y = self_to_local(*touch.pos)
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
