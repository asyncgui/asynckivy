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


class TestApp(App):
    def build(self):
        return Label(font_size=64)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        await ak.n_frames(4)
        label = self.root
        label.text = 'iris_transition'
        touch_down = partial(ak.event, label, 'on_touch_down')
        while True:
            await touch_down()
            async with t.iris_transition(duration=0.8, color=colormap['darkslategray']):
                label.halign = 'center'
                label.text = 'iris_transition\n\nwith a custom overlay'

            await touch_down()
            rect = Rectangle(size=Window.size, source='data/logo/kivy-icon-128.png')
            texture = rect.texture
            texture.wrap = 'repeat'
            x_ratio = Window.width / texture.width
            y_ratio = Window.height / texture.height
            rect.tex_coords = (0, y_ratio, x_ratio, y_ratio, x_ratio, 0, 0, 0)
            async with t.iris_transition(overlay=rect, out_curve='linear', in_curve='linear'):
                await ak.sleep(.3)
                label.text = 'slide_transition'
                await ak.sleep(.3)

            await touch_down()
            async with t.slide_transition(duration=0.6):
                label.halign = 'left'
                label.text = dedent('''
                    slide_transition(
                        x_direction='right',
                        y_direction='up',
                    )''')

            await touch_down()
            async with t.slide_transition(duration=0.6, x_direction='right', y_direction='up'):
                label.text = 'scale_transition'

            await touch_down()
            async with t.scale_transition(duration=0.4):
                label.text = 'fade_transition'

            await touch_down()
            async with t.fade_transition(duration=0.6):
                label.text = 'iris_transition'


if __name__ == '__main__':
    TestApp(title='Transition Showcase').run()
