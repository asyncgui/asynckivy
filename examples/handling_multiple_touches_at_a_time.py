from kivy.uix.relativelayout import RelativeLayout
from kivy.app import runTouchApp
import asynckivy as ak


class Painter(RelativeLayout):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.opos):
            ak.start(self.draw_rect(touch))
            return True
    
    async def draw_rect(self, touch):
        from kivy.graphics import Line, Color, Rectangle
        from kivy.utils import get_random_color
        with self.canvas:
            color = Color(*get_random_color())
            line = Line(width=2)
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
            with self.canvas:
                Color(*get_random_color(alpha=.3))
                Rectangle(
                    pos=(min_x, min_y),
                    size=(max_x - min_x, max_y - min_y, ),
                )
        else:
            self.canvas.remove(color)
            self.canvas.remove(line)
        print('end drawing')

runTouchApp(Painter())
