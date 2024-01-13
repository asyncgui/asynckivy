'''
* The code is intentionally written in an unoptimized way in favor of readability.
* Change the SPLINE_TYPE to switch the spline.
'''
import typing as T
from functools import partial
import array
import math
import random

from kivy.vector import Vector
from kivy.utils import get_random_color
from kivy.graphics import (
    Rectangle, Point, Line, Color, CanvasBase,
    PushMatrix, PopMatrix, Translate, Rotate,
)
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
import asynckivy as ak


SPLINE_TYPE = 'Catmull-Rom'
# SPLINE_TYPE = 'B-Spline'


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
            slp = partial(ak.sleep, 1.0 / speed)

            n_control_points = n_spline_segments + 3
            padding = 30.0
            control_points = generate_random_2d_points(
                n_points=n_control_points,
                min_x=padding, min_y=padding,
                max_x=draw_target.width - padding, max_y=draw_target.height - padding,
            )

            # Draw the control points.
            root_group.add(group1 := CanvasBase())
            with group1:
                color_inst1 = Color(1.0, 1.0, 1.0, 1.0)
                point_inst = Point(pointsize=4.0)
            flattened = array.array('f')
            for p in control_points:
                flattened.extend(p)
                point_inst.points = flattened
                await slp()

            # Draw a polyline that connects the control points.
            with group1:
                color_inst2 = Color(1.0, 1.0, 1.0, 0.0)
                Line(points=flattened)
            await ak.anim_attrs(color_inst2, a=1.0, duration=1.0 / speed)
            await slp()

            # Make the above two darker.
            group1.remove(color_inst2)
            await ak.anim_attrs(color_inst1, r=0.3, g=0.3, b=0.3, duration=1.0 / speed)
            del color_inst2, point_inst, flattened

            n_segments = n_control_points - 3
            interpolating_functions: T.Sequence[T.Tuple[T.Callable, T.Callable]] = tuple(
                (
                    partial(calc_position, f := calc_factors(control_points[i:i + 4])),
                    partial(calc_angle, (f[1], f[2] * 2, f[3] * 3)),
                )
                for i in range(n_segments)
            )

            # Plot points on the spline.
            root_group.add(group2 := CanvasBase())
            with group2:
                color_inst3 = Color(1.0, 1.0, 1.0, 1.0)
                point_inst = Point(pointsize=1.0)
            flattened = array.array('f')
            async for p in ak.anim_with_ratio(duration=n_segments * 2.0 / speed):
                if p >= 1.0:
                    f = interpolating_functions[-1]
                    t = 1.0
                else:
                    idx, t = divmod(p * n_segments, 1.0)
                    f = interpolating_functions[int(idx)]
                flattened.extend(f[0](t))
                point_inst.points = flattened

            # Fade-out the group1, and make the above points darker
            await slp()
            await ak.wait_all(
                ak.anim_attrs(color_inst1, a=0, duration=1.0 / speed),
                ak.anim_attrs(color_inst3, r=0.3, g=0.3, b=0.3, duration=1.0 / speed),
            )
            root_group.remove(group1)
            del color_inst1, color_inst3, point_inst

            # Animate a sprite
            texture = ak.create_texture_from_text(text='@', font_size=80, color=get_random_color())
            with group2:
                Color(1.0, 1.0, 1.0, 1.0)
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
            async for p in ak.anim_with_ratio(duration=n_segments * 2.0 / speed):
                if p >= 1.0:
                    f = interpolating_functions[-1]
                    t = 1.0
                else:
                    idx, t = divmod(p * n_segments, 1.0)
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


if SPLINE_TYPE == 'Catmull-Rom':
    def calc_factors(control_points):
        p0, p1, p2, p3 = control_points
        return (
            p1,
            (p2 - p0) * 0.5,
            p0 + 2 * p2 - 2.5 * p1 - 0.5 * p3,
            (p3 - p0) * 0.5 + (p1 - p2) * 1.5,
        )
elif SPLINE_TYPE == 'B-Spline':
    def calc_factors(control_points):
        p0, p1, p2, p3 = control_points
        return (
            (p0 + p2) / 6.0 + p1 * 2.0 / 3.0,
            (p2 - p0) * 0.5,
            (p0 + p2) * 0.5 - p1,
            (p3 - p0) / 6.0 + (p1 - p2) * 0.5,
        )
else:
    raise ValueError("Invalid SPLINE_TYPE:", SPLINE_TYPE)


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
    SampleApp().run()
