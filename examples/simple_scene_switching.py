'''
For a real-world example, visit https://github.com/gottadiveintopython/whack-a-homole.
'''

from textwrap import dedent
from contextlib import ExitStack
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout

import asynckivy as ak
from asynckivy import transition


burn0_shader = """
// Author: liubailin2020@gmail.com
// License: MIT

uniform vec3 burnColor; // = vec3(1.0, 0.5, 0.0)

float random (in vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

// Based on Morgan McGuire @morgan3d
// https://www.shadertoy.com/view/4dS3Wd
float noise (in vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);

    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) + (c - a)* u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

#define OCTAVES 4
float fbm (in vec2 st) {
    float value = 0.0;
    float amplitude = .5;
    for (int i = 0; i < OCTAVES; i++) {
        value += amplitude * noise(st);
        st *= 2.;
        amplitude *= .5;
    }
    return value;
}

vec4 transition (vec2 uv) {
    if (progress <= 0.0) return getFromColor(uv);
    if (progress >= 1.0) return getToColor(uv);
    vec4 from = getFromColor(uv);
    vec4 to = getToColor(uv);
    float n = fbm(uv * 4.);
    float l = smoothstep(progress, progress + 0.05, n);
    float edge = (1.0 - l) * l * 5.0;
    return mix(to, from, l) + vec4(burnColor, 0.0) * edge;
}
"""


class SampleApp(App):
    def build(self):
        return RelativeLayout()

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        from asynckivy import sceneswitcher
        await sceneswitcher.run(title_scene, transition.fade, parent=self.root, userdata=None)


async def title_scene(parent: RelativeLayout, userdata):
    from math import cos
    with ExitStack() as stack:
        defer = stack.callback

        label = Label(text="Title Scene", font_size=100, bold=True, italic=True)
        parent.add_widget(label)
        defer(parent.remove_widget, label)

        yield

        async with ak.move_on_when(ak.event(label, "on_touch_down")):
            with ak.sleep_freq() as slp:
                et = 0.
                while True:
                    et += await slp()
                    label.opacity = 0.5 + 0.5 * cos(et * 4)

        yield menu_scene, partial(
            transition.gl_transitions_dot_com,
            fs=burn0_shader, duration=2,
            uniforms={"burnColor": (1., 0.5, 0.)},
        )


async def menu_scene(parent: RelativeLayout, userdata, _cache=[]):
    with ExitStack() as stack:
        defer = stack.callback

        if _cache:
            tree = _cache.pop()
        else:
            tree = Builder.load_string(dedent("""
                BoxLayout:
                    orientation: "vertical"
                    padding: 40
                    spacing: 40
                    Label:
                        text: "Menu Scene"
                        font_size: 60
                        bold: True
                        italic: True
                    BoxLayout:
                        spacing: 80
                        Button:
                            id: left_arrow
                            font_size: 100
                            text: "<-"
                        Button:
                            id: right_arrow
                            font_size: 100
                            text: "->"
                    Button:
                        id: back
                        font_size: 48
                        text: "Back to Title"
                """))
        defer(_cache.append, tree)
        parent.add_widget(tree)
        defer(parent.remove_widget, tree)

        yield

        async with ak.move_on_when(ak.event(tree.ids.back, "on_release")):
            while True:
                tasks = await ak.wait_any(
                    ak.event(tree.ids.left_arrow, "on_release"),
                    ak.event(tree.ids.right_arrow, "on_release"),
                )
                with ak.block_touch_events(parent):
                    x_direction = "left" if tasks[0].finished else "right"
                    async with transition.slide(parent, x_direction=x_direction, duration=0.7):
                        pass

        yield title_scene, partial(
            transition.gl_transitions_dot_com,
            fs=burn0_shader, duration=2,
            uniforms={"burnColor": (0., 0.2, 1.)},
        )


if __name__ == "__main__":
    SampleApp(title="SceneSwitcher Demo").run()
