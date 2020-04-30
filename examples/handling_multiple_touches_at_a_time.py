from kivy.uix.relativelayout import RelativeLayout
from kivy.app import runTouchApp
import asynckivy as ak


class Painter(RelativeLayout):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.opos):
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
        ox, oy = self.to_local(*touch.opos)
        on_touch_move_was_fired = False
        async for __ in ak.rest_of_touch_moves(self, touch):
            # Don't await anything during this async-for-loop
            on_touch_move_was_fired = True
            x, y = self.to_local(*touch.pos)
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


if __name__ == "__main__":
    runTouchApp(Painter())
