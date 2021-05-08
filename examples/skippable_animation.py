'''
Skippable Animation
===================

* The ``force_final_value`` argument is intentionally unused
'''

from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak


KV_CODE = r'''
RelativeLayout:
    Label:
        text: 'The animation can be skipped by touching the screen'
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
        ak.start(animate(self.root))


async def animate(root):
    label = root.ids.label.__self__
    while True:
        await ak.or_(
            ak.event(root, 'on_touch_down'),
            ak.animate(label, right=root.width),
        )
        label.right = root.width
        await ak.or_(
            ak.event(root, 'on_touch_down'),
            ak.animate(label, top=root.height),
        )
        label.top = root.height
        await ak.or_(
            ak.event(root, 'on_touch_down'),
            ak.animate(label, x=0),
        )
        label.x = 0
        await ak.or_(
            ak.event(root, 'on_touch_down'),
            ak.animate(label, y=0),
        )
        label.y = 0


if __name__ == '__main__':
    TestApp().run()
