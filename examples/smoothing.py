from random import random, randint
from kivy.event import EventDispatcher
from kivy.graphics import Color, Rectangle, CanvasBase
from kivy.properties import NumericProperty, ReferenceListProperty, ColorProperty
from kivy.app import App
from kivy.uix.widget import Widget
import asynckivy as ak


class AnimatedRectangle(EventDispatcher):
    x = NumericProperty()
    y = NumericProperty()
    pos = ReferenceListProperty(x, y)
    width = NumericProperty()
    height = NumericProperty()
    size = ReferenceListProperty(width, height)
    color = ColorProperty("#FFFFFFFF")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = canvas = CanvasBase()
        with canvas:
            ak.smooth_attr((self, "color"), (Color(self.color), "rgba"), min_diff=0.02, speed=4)
            rect = Rectangle(pos=self.pos, size=self.size)
            ak.smooth_attr((self, "pos"), (rect, "pos"))
            ak.smooth_attr((self, "size"), (rect, "size"))


class SampleApp(App):
    def build(self):
        root = Widget()
        rect = AnimatedRectangle(width=160, height=160)
        root.canvas.add(rect.canvas)

        def on_touch_down(_, touch):
            rect.pos = touch.pos
            rect.color = (random(), random(), random(), 1)
            rect.width = randint(50, 200)
            rect.height = randint(50, 200)
        root.bind(on_touch_down=on_touch_down)
        return root


if __name__ == '__main__':
    SampleApp().run()
