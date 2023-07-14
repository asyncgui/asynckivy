'''
Difference from popping_widget_1.py
-----------------------------------

``Translate`` and ``Rotate`` are inserted into different layers of the canvas, 'canvas.before' and 'canvas'
respectively, so they never interweave each other no matter how much animations are stacked. Try mashing the buttons
and see what happens.
'''
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Rotate, Translate
from asynckivy import vanim, transform


degrees_per_second = float


async def pop_widget(widget, *, height=200., duration=1., rotation_speed: degrees_per_second=360.):
    with transform(widget, use_outer_canvas=True) as outer_ig, transform(widget) as ig:
        translate = Translate()
        outer_ig.add(translate)
        rotate = Rotate(origin=widget.center)
        ig.add(rotate)
        async for dt, et, p in vanim.delta_time_elapsed_time_progress(duration=duration):
            p = p * 2. - 1.  # convert range[0 to +1] into range[-1 to +1]
            translate.y = (-(p * p) + 1.) * height
            rotate.angle = et * rotation_speed


KV_CODE = r'''
#:import ak asynckivy
#:import pop_widget __main__.pop_widget

<CustomButton@Button>:
    size_hint_y: None
    height: '100dp'
    font_size: '100sp'
    on_press: ak.start(pop_widget(self))

BoxLayout:
    spacing: '20dp'
    padding: '20dp'
    CustomButton:
        text: 'A'
    CustomButton:
        pos_hint: {'y': .1, }
        text: 'B'
    CustomButton:
        pos_hint: {'y': .2, }
        text: 'C'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
