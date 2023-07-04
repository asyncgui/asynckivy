'''
* The longer you press the button, the higher it pops.
'''
from contextlib import contextmanager

from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Translate, Scale
from asynckivy import vanim
from asynckivy import transform


@contextmanager
def ignore_touch_down(widget, _f=lambda w, t: w.collide_point(*t.opos)):
    '''Same as the popping_widget_1.py's '''
    uid = widget.fbind('on_touch_down', _f)
    try:
        yield
    finally:
        widget.unbind_uid('on_touch_down', uid)


async def pop_widget(widget, *, max_height=600., max_scale_x=2.0):
    import asynckivy as ak

    if max_scale_x <= 1.0:
        raise ValueError(f"'max_scale_x' must be greater than 1.0. (was {max_scale_x})")
    widget = widget.__self__
    with ignore_touch_down(widget), transform(widget) as ig:
        # phase 1: widget becomes wider and shorter while it being pressed
        scale = Scale(origin=(widget.center_x, widget.y))
        ig.add(scale)
        task = ak.start(ak.animate(scale, x=max_scale_x, y=1.0 / max_scale_x, duration=.5))

        # phase 2: widget becomes thiner and taller when it gets released
        await ak.event(widget, 'on_release')
        task.cancel()
        scale_x = scale.x
        scale_y = scale.y
        await ak.animate(scale, x=scale_y, y=scale_x, duration=0.1)

        # phase 3: widget pops and becomes initial size
        translate = Translate()
        ig.insert(0, translate)
        popping_energy = (scale_x - 1.0) / (max_scale_x - 1.0)
        height = popping_energy * max_height
        ak.start(ak.animate(scale, x=1.0, y=1.0, duration=0.1))
        async for p in vanim.progress(duration=popping_energy):
            p = p * 2. - 1.  # convert range[0 to +1] into range[-1 to +1]
            translate.y = (-(p * p) + 1.) * height
        ig.remove(translate)

        # phase 4: widget becomes wider and shorter on landing
        await ak.animate(scale, x=(scale_x + 1.0) * 0.5, y=(scale_y + 1.0) * 0.5, duration=0.1)

        # phase 5: widget becomes initial size
        await ak.animate(scale, x=1.0, y=1.0, duration=0.1)


KV_CODE = r'''
#:import ak asynckivy
#:import pop_widget __main__.pop_widget

<CustomButton@Button>:
    size_hint_y: None
    height: '100dp'
    font_size: '50sp'
    on_press: ak.start(pop_widget(self))

BoxLayout:
    spacing: '20dp'
    padding: '20dp'
    Widget:
    CustomButton:
        text: "I'm elastic"
    Widget:
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
