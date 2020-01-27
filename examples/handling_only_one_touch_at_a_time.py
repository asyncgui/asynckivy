from kivy.uix.relativelayout import RelativeLayout
from kivy.app import runTouchApp
import asynckivy as ak


class Painter(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ak.start(self.draw_rect())
    
    async def draw_rect(self):
        from kivy.graphics import Line, Color, Rectangle, InstructionGroup
        from kivy.utils import get_random_color
        while True:
            __, touch = await ak.event(
                self, 'on_touch_down',
                filter=lambda w, t: w.collide_point(*t.opos),
                return_value=True,
            )
            inst_group = InstructionGroup()
            self.canvas.add(inst_group)
            inst_group.add(Color(*get_random_color()))
            line = Line(width=2)
            inst_group.add(line)
            ox, oy = touch.opos
            on_touch_move_was_fired = False
            async for __ in ak.all_touch_moves(self, touch):
                # Don't await anything during this async-for-loop or you will
                # lose rest of the touch events.
                on_touch_move_was_fired = True
                x, y = touch.pos
                min_x = min(x, ox)
                min_y = min(y, oy)
                max_x = max(x, ox)
                max_y = max(y, oy)
                line.rectangle = [min_x, min_y, max_x - min_x, max_y - min_y]
            if on_touch_move_was_fired:
                inst_group.add(Color(*get_random_color(alpha=.3)))
                inst_group.add(
                    Rectangle(
                        pos=(min_x, min_y),
                        size=(max_x - min_x, max_y - min_y, ),
                    )
                )
            else:
                self.canvas.remove(inst_group)

runTouchApp(Painter())
