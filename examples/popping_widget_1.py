from contextlib import contextmanager, nullcontext

from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Rotate, Translate
from asynckivy import vanim
from asynckivy.utils import transform


@contextmanager
def ignore_touch_down(widget, _f=lambda w, t: w.collide_point(*t.opos)):
    '''Return a context manager that makes the widget ignore ``on_touch_down`` events that collide with it. This
    is probably useful when you want to disable touch interaction of a widget without changing its appearance.
    (Setting ``disabled`` to True might change the appearance.)
    '''

    uid = widget.fbind('on_touch_down', _f)
    try:
        yield
    finally:
        widget.unbind_uid('on_touch_down', uid)


degrees_per_second = float


async def pop_widget(widget, *, height=300., duration=1., rotation_speed: degrees_per_second=360., ignore_touch=False):
    with ignore_touch_down(widget) if ignore_touch else nullcontext():
        with transform(widget) as ig:  # <- InstructionGroup
            # TODO: refactor after Python 3.7 ends
            translate = Translate()
            rotate = Rotate(origin=widget.center)
            ig.add(translate)
            ig.add(rotate)
            async for dt, et, p in vanim.delta_time_elapsed_time_progress(duration=duration):
                p = p * 2. - 1.  # convert [0 to +1] into [-1 to +1]
                translate.y = (-(p * p) + 1.) * height
                rotate.angle = et * rotation_speed


KV_CODE = r'''
#:import ak asynckivy
#:import pop_widget __main__.pop_widget

<CustomButton@Button>:
    size_hint_y: None
    height: '100dp'
    font_size: '100sp'
    on_press:
        # We don't want to stack animations thus ``ignore_touch=True``.
        ak.start(pop_widget(self, ignore_touch=True))

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
