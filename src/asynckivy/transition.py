__all__ = (
    'fade', 'slide', 'scale', 'iris',
)

from typing import Literal, TypeAlias
from collections.abc import Sequence
from contextlib import asynccontextmanager
import math

from kivy.utils import colormap
from kivy.graphics import (
    Translate, Scale, InstructionGroup, StencilPop, StencilPush, StencilUnUse, StencilUse,
    Rectangle, Ellipse, Color, VertexInstruction, Canvas
)
from kivy.animation import AnimationTransition
from kivy.core.window import Window, WindowBase
from kivy.uix.widget import Widget

from asynckivy import transform, anim_attrs_abbr as anim_attrs


linear = AnimationTransition.linear
Wow: TypeAlias = WindowBase | Widget  # 'Wow' -> WindowBase or Widget


@asynccontextmanager
async def fade(target: Wow | Canvas=Window.canvas, *, goal_opacity=0., duration=1., out_curve=linear, in_curve=linear):
    '''
    .. code-block::

        async with fade(widget):
            ...

    The above code fades out the widget, executes the code inside the with-block, and then fades it back in.
    You can reverse this sequence as follows:

    .. code-block::

        original = widget.opacity
        widget.opacity = 0.
        async with fade(widget, goal_opacity=original):
            ...

    .. versionadded:: 0.9.0
    .. versionchanged:: 0.9.1
        Now accepts Canvas as target.
    '''
    half_d = duration / 2
    original = target.opacity
    try:
        await anim_attrs(target, d=half_d, t=out_curve, opacity=goal_opacity)
        yield
        await anim_attrs(target, d=half_d, t=in_curve, opacity=original)
    finally:
        target.opacity = original


@asynccontextmanager
async def slide(target: Wow=Window, *, duration=1., out_curve='in_back', in_curve='out_back',
                x_direction: Literal['left', 'right', None]='left',
                y_direction: Literal['down', 'up', None]=None,
                use_outer_canvas=False):
    '''
    .. versionadded:: 0.9.0
    .. versionchanged:: 0.9.2
        The default value of ``out_curve`` has changed from ``'in_cubic'`` to ``'in_back'``.
        The default value of ``in_curve`` has changed from ``'out_cubic'`` to ``'out_back'``.
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
        await anim_attrs(mat, d=half_d, t=out_curve, x=x_dist, y=y_dist)
        yield
        mat.x = -x_dist
        mat.y = -y_dist
        await anim_attrs(mat, d=half_d, t=in_curve, x=0, y=0)


@asynccontextmanager
async def scale(target: Wow=Window, *, duration=1, out_curve='out_quad', in_curve='in_quad',
                use_outer_canvas=False):
    '''
    .. versionadded:: 0.9.0
    '''
    with transform(target, use_outer_canvas=use_outer_canvas) as ig:
        ig.add(mat := Scale(origin=target.center))
        half_d = duration / 2
        await anim_attrs(mat, d=half_d, t=out_curve, xyz=(0, 0, 1))
        yield
        await anim_attrs(mat, d=half_d, t=in_curve, xyz=(1, 1, 1))


def _calc_enclosing_circle_radius(circle_center, rectangle_size, max=max, hypot=math.hypot, abs=abs):
    '''
    Calculates the minimum radius required for a circle centered at the given position to fully
    enclose a rectangle of the given size, assuming its bottom-left corner is at (0, 0).

    .. code-block::

        radius = _calc_enclosing_circle_radius(circle_center, rectangle_size)
    '''
    w, h = rectangle_size
    x, y = circle_center
    return hypot(max(abs(x), abs(w - x)), max(abs(y), abs(h - y)))


@asynccontextmanager
async def iris(target: WindowBase=Window, *, duration=1, out_curve='in_cubic', in_curve='out_cubic',
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
    ig_add(inner_ig)
    ig_add(StencilPop())

    canvas.add(ig)
    try:
        await anim_attrs(ellipse, d=half_d, t=out_curve, pos=circle_center, size=(0, 0))
        # Setting the ellipse size to (0, 0) isn't enough to nullify the stencil effect for some reason,
        # so we remove it from the canvas and re-add it later.
        inner_ig.remove(ellipse)
        yield
        inner_ig.add(ellipse)
        await anim_attrs(ellipse, d=half_d, t=in_curve, pos=ellipse_start_pos, size=ellipse_start_size)
    finally:
        canvas.remove(ig)


# Aliases for backward compatibility
fade_transition = fade
slide_transition = slide
scale_transition = scale
iris_transition = iris
