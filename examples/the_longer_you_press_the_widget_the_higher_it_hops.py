from functools import partial

from kivy.metrics import cm
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Translate, Scale
import asynckivy as ak


GRAVITY = -9.80665 * cm(100)
ignore_touch_down = partial(ak.suppress_event, event_name='on_touch_down', filter=lambda w, t: w.collide_point(*t.opos))


async def bounce_widget(widget, *, scale_x_max=3.0, gravity_factor=0.2):
    import asynckivy as ak
    from asynckivy import vanim

    if scale_x_max <= 1.0:
        raise ValueError(f"'scale_x_max' must be greater than 1.0. (was {scale_x_max})")
    if gravity_factor <= 0:
        raise ValueError(f"'gravity_factor' must be greater than 0. (was {gravity_factor})")
    widget = widget.__self__
    with ignore_touch_down(widget), ak.transform(widget) as ig:
        # phase 1: Widget becomes wider and shorter while it being pressed.
        scale = Scale(origin=(widget.center_x, widget.y))
        ig.add(scale)
        async with ak.run_as_secondary(ak.animate(scale, x=scale_x_max, y=1.0 / scale_x_max, duration=0.25 * scale_x_max)):
            await ak.event(widget, 'on_release')

        # phase 2: Widget becomes thiner and taller after it got released.
        scale_x = scale.x
        scale_y = scale.y
        await ak.animate(scale, x=scale_y, y=scale_x, duration=0.1)

        # phase 3: Widget bounces and returns to its original size.
        ig.insert(0, translate := Translate())
        initial_velocity = scale_x ** 2 * 1000.0
        gravity = GRAVITY * gravity_factor
        async with ak.wait_all_cm(ak.animate(scale, x=1.0, y=1.0, duration=0.1)):
            async for et in vanim.elapsed_time():
                translate.y = y = et * (initial_velocity + gravity * et)
                if y <= 0:
                    break
        ig.remove(translate)

        # phase 4: Widget becomes wider and shorter on landing.
        await ak.animate(scale, x=(scale_x + 1.0) * 0.5, y=(scale_y + 1.0) * 0.5, duration=0.1)

        # phase 5: Widget returns to its original size.
        await ak.animate(scale, x=1.0, y=1.0, duration=0.1)


KV_CODE = r'''
#:import ak asynckivy
#:import bounce_widget __main__.bounce_widget

<Puyo@ButtonBehavior+Widget>:
    always_release: True
    on_press: ak.start(bounce_widget(self))
    canvas:
        PushMatrix:
        Translate:
            xy: self.center
        Scale:
            xyz: (*self.size, 1.0, )
        Color:
            rgba: (1, 1, 1, 1, )
        Line:
            width: 0.01
            circle: 0, 0, 0.5
        Line:
            width: 0.01
            circle: 0.2, 0.18, 0.15
        Ellipse:
            pos: 0.2 - 0.01, 0.18 - 0.01
            size: 0.1, 0.1
        Line:
            width: 0.01
            circle: -0.2, 0.18, 0.15
        Ellipse:
            pos: -0.2 - 0.01, 0.18 - 0.01
            size: 0.1, 0.1
        PopMatrix:

BoxLayout:
    spacing: '20dp'
    padding: '20dp'
    Widget:
    Puyo:
        size_hint: None, None
        size: '200dp', '170dp'
    Widget:
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp(title='The longer you press the widget, the higher it hops').run()
