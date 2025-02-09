import itertools
from kivy.app import App
from kivy.graphics import Line, Color, InstructionGroup
import asynckivy as ak


async def progress_spinner(
        *, draw_target: InstructionGroup, center, radius, line_width=10, color=(1, 1, 1, 1, ), min_arc_angle=40,
        speed=1.0):

    BS = 40.0  # base speed (in degrees)
    AS = 360.0 - min_arc_angle * 2
    get_next_start = itertools.accumulate(itertools.cycle((BS, BS, BS + AS, BS, )), initial=0).__next__
    get_next_stop = itertools.accumulate(itertools.cycle((BS + AS, BS, BS, BS, )), initial=min_arc_angle).__next__
    d = 0.4 / speed
    start = get_next_start()
    stop = get_next_stop()
    draw_target.add(color_inst := Color(*color))
    draw_target.add(line_inst := Line(width=line_width))
    try:
        line_inst.circle = (*center, radius, start, stop)
        while True:
            next_start = get_next_start()
            next_stop = get_next_stop()
            async for sta, sto in ak.interpolate_seq((start, stop), (next_start, next_stop), duration=d):
                line_inst.circle = (*center, radius, sta, sto)
            start = next_start
            stop = next_stop
    finally:
        draw_target.remove(line_inst)
        draw_target.remove(color_inst)


class TestApp(App):
    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        await ak.n_frames(4)
        root = self.root
        await progress_spinner(
            draw_target=root.canvas,
            center=root.center,
            radius=min(root.size) * 0.4,
        )


if __name__ == '__main__':
    TestApp(title="Progress Spinner").run()
