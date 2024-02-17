'''
* The code is intentionally written in an unoptimized way in favor of readability.
'''
import typing as T
import math
import random
import itertools
from functools import partial

from kivy.vector import Vector
from kivy.utils import get_random_color
from kivy.graphics import (
    Rectangle, Point, Line, Color, CanvasBase,
    PushMatrix, PopMatrix, Translate, Rotate,
)
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
import asynckivy as ak


class SampleApp(App):
    def build(self):
        return RelativeLayout()

    def on_start(self):
        ak.start(self.main())

    async def main(self):
        await ak.n_frames(2)
        while True:
            await self.play_animation(draw_target=self.root, speed=2.0, n_spline_segments=3)

    async def play_animation(self, *, draw_target, speed=1.0, n_spline_segments):
        draw_target.canvas.add(root_group := CanvasBase())
        try:
            n_control_points = n_spline_segments + 3
            padding = 30.0
            control_points = generate_random_2d_points(
                n_points=n_control_points,
                min_x=padding, min_y=padding,
                max_x=draw_target.width - padding, max_y=draw_target.height - padding,
            )
            flattened = tuple(itertools.chain.from_iterable(control_points))
            texture = ak.create_texture_from_text(text='@', font_size=80, color=get_random_color())
            interpolating_functions: T.Sequence[T.Tuple[T.Callable, T.Callable]] = tuple(
                (
                    partial(calc_position, f := calc_factors(control_points[i:i + 4])),
                    partial(calc_angle, (f[1], f[2] * 2, f[3] * 3)),
                )
                for i in range(n_spline_segments)
            )

            with root_group:
                Color(1.0, 1.0, 1.0, 1.0)
                Point(pointsize=4.0, points=flattened)
                Line(points=flattened)
                PushMatrix()
                f = interpolating_functions[0]
                translate = Translate(*f[0](0))
                rotate = Rotate()
                rotate.angle = rotate.angle = f[1](0)
                Rectangle(
                    pos=(-texture.width / 2, -texture.height / 2, ),
                    size=texture.size,
                    texture=texture,
                )
                PopMatrix()
            await ak.sleep(1.0 / speed)
            async for p in ak.anim_with_ratio(duration=n_spline_segments * 2.0 / speed):
                if p >= 1.0:
                    f = interpolating_functions[-1]
                    t = 1.0
                else:
                    idx, t = divmod(p * n_spline_segments, 1.0)
                    f = interpolating_functions[int(idx)]
                x, y = f[0](t)
                translate.x = x
                translate.y = y
                rotate.angle = f[1](t)
            await ak.sleep(1)
        finally:
            draw_target.canvas.remove(root_group)


def generate_random_2d_points(*, n_points, min_x, min_y, max_x, max_y) -> T.Sequence[Vector]:
    r = random.random
    width = max_x - min_x
    height = max_y - min_y
    return tuple(
        Vector(r() * width + min_x, r() * height + min_y)
        for __ in range(n_points)
    )


def calc_factors(control_points):
    p0, p1, p2, p3 = control_points
    return (
        p1,
        (p2 - p0) * 0.5,
        p0 + 2 * p2 - 2.5 * p1 - 0.5 * p3,
        (p3 - p0) * 0.5 + (p1 - p2) * 1.5,
    )


def calc_position(factors, t):
    f0, f1, f2, f3 = factors
    t2 = t * t
    t3 = t2 * t
    return f0 + t * f1 + t2 * f2 + t3 * f3


def calc_velocity(factors, t):
    f1, f2, f3 = factors
    t2 = t * t
    return f1 + t * f2 + t2 * f3


def calc_angle(factors, t):
    vel_x, vel_y = calc_velocity(factors, t)
    return math.degrees(math.atan2(vel_y, vel_x))


if __name__ == '__main__':
    SampleApp(title="Moving a aprite along with a Catmull-Rom spline").run()
