'''
https://youtu.be/qehA3oIMXZo
'''
from textwrap import dedent
from functools import partial

from kivy.utils import colormap
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.label import Label

import asynckivy as ak
from asynckivy import transition as t


cross_warp = '''
// https://gl-transitions.com/editor/crosswarp

// Author: Eke Péter <peterekepeter@gmail.com>
// License: MIT
vec4 transition(vec2 p) {
  float x = progress;
  x=smoothstep(.0,1.0,(x*2.0+p.x-1.0));
  return mix(getFromColor((p-.5)*(1.-x)+.5), getToColor((p-.5)*x+.5), x);
}
'''


class TestApp(App):
    def build(self):
        return Label(font_size=64)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        await ak.n_frames(4)
        label = self.root
        label.halign = 'center'
        label.text = 'crosswarp\n(from gl-transitions.com)'
        touch_down = partial(ak.event, label, 'on_touch_down')
        while True:
            await touch_down()
            async with t.gl_transitions_dot_com(label, fs=cross_warp):
                label.text = 'iris'

            await touch_down()
            async with t.iris(duration=0.8, color=colormap['darkslategray']):
                label.halign = 'center'
                label.text = 'iris with a custom overlay'

            await touch_down()
            rect = Rectangle(size=Window.size, source='data/logo/kivy-icon-128.png')
            texture = rect.texture
            texture.wrap = 'repeat'
            x_ratio = Window.width / texture.width
            y_ratio = Window.height / texture.height
            rect.tex_coords = (0, y_ratio, x_ratio, y_ratio, x_ratio, 0, 0, 0)
            async with t.iris(overlay=rect, out_curve='linear', in_curve='linear'):
                await ak.sleep(.3)
                label.text = 'slide'
                await ak.sleep(.3)

            await touch_down()
            async with t.slide(duration=0.6):
                label.halign = 'left'
                label.text = dedent('''
                    slide(
                        x_direction='right',
                        y_direction='up',
                    )''')

            await touch_down()
            async with t.slide(duration=0.6, x_direction='right', y_direction='up'):
                label.text = 'scale'

            await touch_down()
            async with t.scale(duration=0.4):
                label.text = 'fade'

            await touch_down()
            async with t.fade(duration=0.6):
                label.halign = 'center'
                label.text = 'crosswarp\n(from gl-transitions.com)'


if __name__ == '__main__':
    TestApp(title='Transition Showcase').run()
