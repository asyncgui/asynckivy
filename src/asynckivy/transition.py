__all__ = (
    'fade_transition', 'slide_transition', 'scale_transition', 'iris_transition',
)

from typing import Literal, Union
from collections.abc import Sequence
from contextlib import asynccontextmanager
import math

from kivy.utils import colormap
from kivy.graphics import (
    Translate, Scale, InstructionGroup, StencilPop, StencilPush, StencilUnUse, StencilUse,
    Rectangle, Ellipse, Color, VertexInstruction
)
from kivy.animation import AnimationTransition
from kivy.core.window import Window, WindowBase
from kivy.uix.widget import Widget

from asynckivy import anim_attrs_abbr, transform


linear = AnimationTransition.linear
Wow = Union[WindowBase, Widget]  # 'Wow' -> WindowBase or Widget


@asynccontextmanager
async def fade_transition(target: Wow=Window, *, duration=1, out_curve=linear, in_curve=linear):
    '''
    .. versionadded:: 0.9.0
    '''
    half_d = duration / 2
    canvas = target.canvas
    orig = canvas.opacity
    try:
        await anim_attrs_abbr(canvas, d=half_d, t=out_curve, opacity=0)
        yield
        await anim_attrs_abbr(canvas, d=half_d, t=in_curve, opacity=orig)
    finally:
        canvas.opacity = orig


@asynccontextmanager
async def slide_transition(target: Wow=Window, *, duration=1, out_curve='in_cubic', in_curve='out_cubic',
                           x_direction: Literal['left', 'right', None]='left',
                           y_direction: Literal['down', 'up', None]=None,
                           use_outer_canvas=False):
    '''
    .. versionadded:: 0.9.0
    '''
    x_dist, y_dist = target.size
    if x_direction is None:
        x_dist = 0
    elif x_direction == 'left':
        x_dist = -x_dist
    if y_direction is None:
        y_dist = 0
    elif y_direction == 'down':
        y_dist = -y_dist

    with transform(target, use_outer_canvas=use_outer_canvas) as ig:
        ig.add(mat := Translate())
        half_d = duration / 2
        await anim_attrs_abbr(mat, d=half_d, t=out_curve, x=x_dist, y=y_dist)
        yield
        mat.x = -x_dist
        mat.y = -y_dist
        await anim_attrs_abbr(mat, d=half_d, t=in_curve, x=0, y=0)


@asynccontextmanager
async def scale_transition(target: Wow=Window, *, duration=1, out_curve='out_quad', in_curve='in_quad',
                           use_outer_canvas=False):
    '''
    .. versionadded:: 0.9.0
    '''
    with transform(target, use_outer_canvas=use_outer_canvas) as ig:
        ig.add(mat := Scale(origin=target.center))
        half_d = duration / 2
        await anim_attrs_abbr(mat, d=half_d, t=out_curve, xyz=(0, 0, 1))
        yield
        await anim_attrs_abbr(mat, d=half_d, t=in_curve, xyz=(1, 1, 1))


def _calc_enclosing_circle_radius(circle_center, rectangle_size, max=max, hypot=math.hypot, abs=abs):
    '''
    Calculates the minimum radius required for a circle centered at the specified position to fully
    enclose a rectangle of the given size, assuming its bottom-left corner is at (0, 0).

    .. code-block::

        radius = _calc_enclosing_circle_radius(circle_center, rectangle_size)
    '''
    w, h = rectangle_size
    x, y = circle_center
    return hypot(max(abs(x), abs(w - x)), max(abs(y), abs(h - y)))


@asynccontextmanager
async def iris_transition(target: WindowBase=Window, *, duration=1, out_curve='in_cubic', in_curve='out_cubic',
                          color: Sequence[float]=colormap['white'], circle_center: Sequence[float]=None,
                          overlay: VertexInstruction=None):
    '''
    .. versionadded:: 0.9.0
    '''
    if not isinstance(target, WindowBase):
        raise TypeError(f"'target' must be a WindowBase instance, not {type(target).__name__}")
    half_d = duration / 2
    canvas = target.canvas
    if circle_center is None:
        circle_center = target.center
    if overlay is None:
        overlay = Rectangle(size=target.size)
    radius = _calc_enclosing_circle_radius(circle_center, target.size)
    diameter = radius * 2.
    ellipse_start_pos = (circle_center[0] - radius, circle_center[1] - radius)
    ellipse_start_size = (diameter, diameter)
    ig = InstructionGroup()
    ig_add = ig.add
    ig_add(StencilPush())
    ig_add(inner_ig := InstructionGroup())
    inner_ig.add(ellipse := Ellipse(pos=ellipse_start_pos, size=ellipse_start_size))
    ig_add(overlay)
    ig_add(StencilUse())
    ig_add(Color(*color))
    ig_add(overlay)
    ig_add(StencilUnUse())
    ig_add(overlay)
    ig_add(ellipse)
    ig_add(StencilPop())

    canvas.add(ig)
    try:
        await anim_attrs_abbr(ellipse, d=half_d, t=out_curve, pos=circle_center, size=(0, 0))
        # Setting the ellipse size to (0, 0) isn't enough to nullify the stencil effect for some reason,
        # so we remove it from the canvas and re-add it later.
        inner_ig.remove(ellipse)
        yield
        inner_ig.add(ellipse)
        await anim_attrs_abbr(ellipse, d=half_d, t=in_curve, pos=ellipse_start_pos, size=ellipse_start_size)
    finally:
        canvas.remove(ig)
