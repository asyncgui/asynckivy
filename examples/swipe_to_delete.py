'''
https://youtu.be/T5mZPIsK9-o
'''

from functools import partial
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Translate
from kivy.uix.button import Button
import asynckivy as ak


async def swipe_to_delete(layout, *, swipe_distance=400.):
    '''
    指定されたlayoutの子widget達をスワイプ操作で取り除けるようにする。
    この効力があるのはこの関数の実行中のみであり、それが終わり次第layoutは元の状態に戻る。
    また実行中はlayoutへ伝わるはずのtouchイベントを全て遮る。
    '''
    layout = layout.__self__
    is_recycle_type = hasattr(layout, 'recycleview')
    se = partial(ak.suppress_event, layout, filter=lambda w, t: w.collide_point(*t.pos))
    with se("on_touch_down"), se("on_touch_move"), se("on_touch_up"):
        while True:
            __, touch = await ak.event(layout, "on_touch_down")
            # 'layout.to_local()' here is not necessary for this particular example to work because the 'layout' is an
            # instance of BoxLayout and the BoxLayout is not a relative type widget.
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
                        if is_recycle_type:
                            layout.recycleview.data.pop(layout.get_view_index_at(c.center))
                        else:
                            layout.remove_widget(c)
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
        self._main_task = ak.start(self.main())

    def on_stop(self):
        self._main_task.cancel()

    async def main(self):
        ids = self.root.ids
        switch = ids.switch
        container = ids.container
        while True:
            await ak.event(switch, 'active', filter=lambda _, active: active)
            async with ak.run_as_main(ak.event(switch, 'active')):
                await swipe_to_delete(container)


if __name__ == '__main__':
    SampleApp(title='Swipe to Delete').run()
