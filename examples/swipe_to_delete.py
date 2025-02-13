'''
https://youtu.be/T5mZPIsK9-o
'''

from functools import partial
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Translate
from kivy.uix.button import Button
import asynckivy as ak


def remove_child(layout, child):
    layout.remove_widget(child)


async def enable_swipe_to_delete(target_layout, *, swipe_distance=400., delete_action=remove_child):
    '''
    Enables swipe-to-delete functionality for a layout. While enabled, the API blocks all touch
    events that intersect with the layout, meaning that if there is a button inside the layout,
    the user cannot press it.

    :param delete_action: You can replace the default deletion action by passing a custom function.
    '''
    layout = target_layout.__self__
    se = partial(ak.suppress_event, layout, filter=lambda w, t: w.collide_point(*t.pos))
    with se("on_touch_down"), se("on_touch_move"), se("on_touch_up"):
        while True:
            __, touch = await ak.event(layout, "on_touch_down")
            # 'layout.to_local()' here is not necessary for this example to work because the 'layout' is an
            # instance of BoxLayout, and the BoxLayout is not a relative-type widget.
            ox, oy = layout.to_local(*touch.opos)
            for c in layout.children:
                if c.collide_point(ox, oy):
                    break
            else:
                continue
            try:
                ox = touch.ox
                with ak.transform(c) as ig:
                    ig.add(translate := Translate())
                    async for __ in ak.rest_of_touch_events(layout, touch):
                        translate.x = dx = touch.x - ox
                        c.opacity = 1.0 - abs(dx) / swipe_distance
                    if c.opacity < 0.3:
                        delete_action(layout, c)
            finally:
                c.opacity = 1.0


KV_CODE = r'''
BoxLayout:
    spacing: '10dp'
    padding: '10dp'
    orientation: 'vertical'
    Switch:
        id: switch
        active: False
        size_hint_y: None
        height: '50dp'
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
            add_widget(Button(text=str(i), size_hint_y=None, height='50dp'))
        return root

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        ids = self.root.ids
        switch = ids.switch
        container = ids.container
        while True:
            await ak.event(switch, 'active', filter=lambda _, active: active)
            async with ak.run_as_main(ak.event(switch, 'active')):
                await enable_swipe_to_delete(container)


if __name__ == '__main__':
    SampleApp(title='Swipe to Delete').run()
