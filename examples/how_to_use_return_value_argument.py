from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch') 
from kivy.app import App
from kivy.lang import Builder
import asynckivy


KV_CODE = '''
BoxLayout:
    Button:
        text: "This button can't be pressed while drawing"
    FloatLayout:
        Label:
            text:
                (
                "left-click to start drawing poly-line\\n"
                "right-click to finish current poly-line"
                )
            pos_hint: {'x': 0, 'y': 0, }
        Widget:
            id: canvas_widget
            pos_hint: {'x': 0, 'y': 0, }
'''


class TestApp(App):

    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        from kivy.graphics import Line, Color
        from kivy.utils import get_random_color
        canvas_widget = self.root.ids.canvas_widget
        async def handle_touch(widget):
            event = asynckivy.event
            while True:
                __, touch = await event(
                    widget, 'on_touch_down',
                    filter=lambda w, touch: w.collide_point(*touch.opos) and touch.button == 'left')
                print('start drawing poly-line')
                with widget.canvas:
                    Color(*get_random_color())
                    line = Line(points=[*touch.opos], width=2)
                while True:
                    __, touch = await event(
                        widget, 'on_touch_down', return_value=True)
                    if touch.button == 'left':
                        line.points.extend(touch.pos)
                        line.points = line.points
                    elif touch.button == 'right':
                        print('end drawing poly-line')
                        break
        asynckivy.start(handle_touch(canvas_widget))


if __name__ == '__main__':
    TestApp().run()