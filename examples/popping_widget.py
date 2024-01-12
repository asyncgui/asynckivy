from contextlib import nullcontext
from functools import partial

from kivy.config import Config
Config.set('modules', 'showborder', '')
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Rotate, Translate
from asynckivy import anim_with_dt_et_ratio, transform, suppress_event


ignore_touch_down = partial(suppress_event, event_name='on_touch_down', filter=lambda w, t: w.collide_point(*t.opos))
'''
.. code-block::

    with ignore_touch_down(widget):
        ...

Returns a context manager that causes a specified ``widget`` to ignore ``on_touch_down`` events that intersect with it.
This can be particularly useful when you need to disable touch interaction for a widget without altering its
appearance. (Setting the ``disabled`` property to True might alter the appearance.)
'''


degrees_per_second = float


async def pop_widget(widget, *, height=300., duration=1., rotation_speed: degrees_per_second=360., ignore_touch=False):
    with ignore_touch_down(widget) if ignore_touch else nullcontext(), transform(widget) as ig:  # <- InstructionGroup
        translate = Translate()
        rotate = Rotate(origin=widget.center)
        ig.add(translate)
        ig.add(rotate)
        async for dt, et, p in anim_with_dt_et_ratio(duration=duration):
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
    on_press:
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
    SampleApp(title='popping widget').run()
