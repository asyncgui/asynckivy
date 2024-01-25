'''
https://youtu.be/T5mZPIsK9-o
'''

from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Translate
from kivy.uix.button import Button
import asynckivy as ak


async def swipe_to_delete(layout, *, swipe_distance=400.):
    layout = layout.__self__
    while True:
        __, touch = await ak.event(layout, "on_touch_down", stop_dispatching=True)
        ox, oy = touch.opos
        for c in layout.children:
            if c.collide_point(ox, oy):
                break
        else:
            continue
        try:
            with ak.transform(c) as ig:
                ig.add(translate := Translate())
                async for __ in ak.rest_of_touch_events(layout, touch, stop_dispatching=True):
                    distance = touch.x - ox
                    translate.x = distance
                    c.opacity = 1.0 - abs(distance) / swipe_distance
                if c.opacity < 0.3:
                    layout.remove_widget(c)
        finally:
            c.opacity = 1.0


KV_CODE = r'''
#:import ak asynckivy
#:import swipe_to_delete __main__.swipe_to_delete

BoxLayout:
    spacing: '10dp'
    padding: '10dp'
    orientation: 'vertical'
    Label:
        text: 'swipe to_delete'
        color: 1, 1, 0, 1
        size_hint_y: None
        height: 50
    Switch:
        active: False
        on_active:
            (
            setattr(root, '_swipe_task', ak.start(swipe_to_delete(container)))
            if args[1] else
            root._swipe_task.cancel()
            )
        size_hint_y: None
        height: 50
    ScrollView:
        BoxLayout:
            id: container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: '10dp'
'''


class SampleApp(App):
    def build(self):
        root = Builder.load_string(KV_CODE)
        add_widget = root.ids.container.add_widget
        for i in range(20):
            add_widget(Button(text=str(i), size_hint_min_y=50))
        return root


if __name__ == '__main__':
    SampleApp(title='swipe to delete').run()
