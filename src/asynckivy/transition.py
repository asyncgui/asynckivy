__all__ = (
    'fade', 'slide', 'scale', 'iris', 'shader', 'gl_transitions_dot_com',
)

from typing import Literal, TypeAlias, Union
from collections.abc import Sequence, Mapping
from contextlib import asynccontextmanager, ExitStack
import math
import string

from kivy.utils import colormap
from kivy.graphics.texture import Texture
from kivy.graphics import (
    Translate, Scale, InstructionGroup, StencilPop, StencilPush, StencilUnUse, StencilUse,
    Rectangle, Ellipse, Color, VertexInstruction, Canvas, BindTexture, Fbo, RenderContext,
)
from kivy.animation import AnimationTransition
from kivy.core.window import Window, WindowBase
from kivy.uix.widget import Widget

import asynckivy as ak
from asynckivy import transform, anim_attrs_abbr as anim_attrs


linear = AnimationTransition.linear
Wow: TypeAlias = Union[WindowBase, Widget]  # 'Wow' -> WindowBase or Widget


@asynccontextmanager
async def fade(target: Wow | Canvas=Window.canvas, *, goal_opacity=0., duration=1., out_curve=linear, in_curve=linear):
    '''
    Fades out the ``target``, executes the code inside the with-block, and then fades it back in.

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
    Slides the ``target`` out, executes the code inside the with-block, and then slides it back in.

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
    Shrinks the ``target``, executes the code inside the with-block, and then restores it to its original size.

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
    縮む円によって ``target`` が見える範囲を絞っていき、完全に見えなくなったらwithブロック内を実行し、その後円を広げて ``target`` を再び見せる。

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


def _render_to_texture(widget) -> Texture:
    fbo = Fbo(size=widget.size)
    fbo.children.extend(
        (Translate(-widget.x, -widget.y, 0.), widget.canvas, )
    )
    fbo.draw()
    fbo.children.clear()
    return fbo.texture


@asynccontextmanager
async def shader(target: Widget, fs: str, *, duration=1., uniforms: Mapping=None,
                 progress_var: str='progress', out_texture_var: str='out_tex', in_texture_var: str='in_tex'):
    '''
    A transition that uses a GLSL fragment shader.

    .. code-block::

        fade = """
        /* Outputs from the vertex shader */
        varying vec4 frag_color;
        varying vec2 tex_coord0;

        uniform float t;
        uniform sampler2D out_tex;
        uniform sampler2D in_tex;

        void main(void) {
            vec4 cout = texture2D(out_tex, tex_coord0);
            vec4 cin = texture2D(in_tex, tex_coord0);
            gl_FragColor = mix(cout, cin, t);
        }
        """

        async with shader(widget, fs=fade, progress_var='t', out_texture_var='out_tex', in_texture_var='in_tex'):
            ...

    :param fs: The GLSL fragment shader code to use.
    :param progress_var: Name of the uniform ``float`` variable representing the normalized progress
                         (elapsed time divided by ``duration``).
    :param out_texture_var: Name of the uniform ``sampler2D`` variable for the *outgoing* texture.
                            This corresponds to the rendered content of the target before ``__aenter__``.
    :param in_texture_var: Name of the uniform ``sampler2D`` variable for the *incoming* texture.
                           This corresponds to the rendered content of the target before ``__aexit__``.
    :param uniforms: Additional uniform variables to be set on the shader.

    .. warning::
        Do not modify the target's parent — such as adding or removing widgets or graphics instructions — while the
        transition is in progress. Modifying the target itself is fine.
    .. versionadded:: 0.9.3
    '''
    parent_canvas = target.parent.canvas
    original_idx = parent_canvas.children.index(target.canvas)

    with ExitStack() as stack:
        parent_canvas.remove(target.canvas)
        stack.callback(parent_canvas.insert, original_idx, target.canvas)
        out_texture = _render_to_texture(target)
        ig = InstructionGroup()
        parent_canvas.insert(original_idx, ig)
        try:
            ig.add(Color())
            ig.add(rect := Rectangle(size=target.size, pos=target.pos, texture=out_texture))
            yield
            await ak.sleep(0)
        finally:
            parent_canvas.remove(ig)
            ig.clear()

        in_texture = _render_to_texture(target)
        rc = RenderContext(fs=fs, use_parent_projection=True, use_parent_modelview=True)
        if not rc.shader.success:
            raise ValueError('Failed to set shader')
        parent_canvas.insert(original_idx, rc)
        stack.callback(parent_canvas.remove, rc)
        rc.add(BindTexture(texture=out_texture, index=1))
        rc.add(BindTexture(texture=in_texture, index=2))
        rect.texture = None
        rc.add(rect)
        rc[out_texture_var] = 1
        rc[in_texture_var] = 2
        rc[progress_var] = elapsed_time = 0.
        if uniforms:
            for k, v in uniforms.items():
                rc[k] = v

        async with ak.sleep_freq() as sleep:
            while elapsed_time < duration:
                elapsed_time += await sleep()
                rc[progress_var] = elapsed_time / duration


GL_TRANSITIONS_DOT_COM_TEMPLATE = string.Template('''
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

uniform float progress;
uniform sampler2D out_tex;
uniform sampler2D in_tex;

vec4 getFromColor(vec2 uv) {
    return texture2D(out_tex, uv);
}
vec4 getToColor(vec2 uv) {
    return texture2D(in_tex, uv);
}

${usercode}

void main(void) {
    gl_FragColor = transition(tex_coord0);
}
''')


def gl_transitions_dot_com(target: Widget, fs: str, *, duration=1., uniforms: Mapping=None):
    '''
    A transition that uses a GLSL fragment shader from https://gl-transitions.com/.

    .. code-block::

        cross_warp = """
        // Author: Eke Péter <peterekepeter@gmail.com>
        // License: MIT
        vec4 transition(vec2 p) {
            float x = progress;
            x=smoothstep(.0,1.0,(x*2.0+p.x-1.0));
            return mix(getFromColor((p-.5)*(1.-x)+.5), getToColor((p-.5)*x+.5), x);
        }
        """

        async with gl_transitions_dot_com(widget, fs=cross_warp):
            ...

    See :func:`shader` for details.

    .. versionadded:: 0.9.3
    '''
    return shader(
        target,
        GL_TRANSITIONS_DOT_COM_TEMPLATE.substitute(usercode=fs),
        progress_var='progress',
        out_texture_var='out_tex',
        in_texture_var='in_tex',
        duration=duration,
        uniforms=uniforms,
    )


# Aliases for backward compatibility
fade_transition = fade
slide_transition = slide
scale_transition = scale
iris_transition = iris
