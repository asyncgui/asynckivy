'''
Skippable Animation
===================
'''

from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak


KV_CODE = r'''
RelativeLayout:
    Label:
        text: 'This animation can be skipped by touching the screen'
    Label:
        id: label
        size_hint: None, None
        size: self.texture_size
        text: 'Label'
        font_size: '80sp'
'''


class TestApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        from asynckivy import wait_any, event, anim_attrs
        root = self.root
        label = root.ids.label.__self__
        while True:
            await wait_any(
                event(root, 'on_touch_down'),
                anim_attrs(label, right=root.width),
            )
            label.right = root.width
            await wait_any(
                event(root, 'on_touch_down'),
                anim_attrs(label, top=root.height),
            )
            label.top = root.height
            await wait_any(
                event(root, 'on_touch_down'),
                anim_attrs(label, x=0),
            )
            label.x = 0
            await wait_any(
                event(root, 'on_touch_down'),
                anim_attrs(label, y=0),
            )
            label.y = 0


if __name__ == '__main__':
    TestApp(title="Skippable Animation").run()
