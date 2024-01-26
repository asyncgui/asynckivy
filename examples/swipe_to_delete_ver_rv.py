from functools import partial
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Translate
import asynckivy as ak


async def swipe_to_delete(layout, *, swipe_distance=400.):
    layout = layout.__self__
    se = partial(ak.suppress_event, layout, filter=lambda w, t: w.collide_point(*t.pos))
    with se("on_touch_down"), se("on_touch_move"), se("on_touch_up"):
        while True:
            __, touch = await ak.event(layout, "on_touch_down")
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
                        layout.recycleview.data.pop(layout.get_view_index_at(c.center))
            finally:
                c.opacity = 1.0


KV_CODE = r'''
#:import ak asynckivy
#:import swipe_to_delete __main__.swipe_to_delete

BoxLayout:
    spacing: '10dp'
    padding: '10dp'
    orientation: 'vertical'
    Switch:
        active: False
        on_active:
            (
            setattr(container, '_swipe_to_delete_task', ak.start(swipe_to_delete(container)))
            if args[1] else
            container._swipe_to_delete_task.cancel()
            )
        size_hint_y: None
        height: '50dp'
    RecycleView:
        data: [{'text': str(i), } for i in range(200)]
        viewclass: 'Button'
        RecycleBoxLayout:
            id: container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: '10dp'
            default_size_hint: 1, 1
            default_size_hint_y_min: '50dp'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp(title='Swipe to Delete (RecycleView)').run()
