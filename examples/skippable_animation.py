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
        ak.start(self.main())

    async def main(self):
        from asynckivy import or_, event, animate
        root = self.root
        label = root.ids.label.__self__
        while True:
            await or_(
                event(root, 'on_touch_down'),
                animate(label, right=root.width),
            )
            label.right = root.width
            await or_(
                event(root, 'on_touch_down'),
                animate(label, top=root.height),
            )
            label.top = root.height
            await or_(
                event(root, 'on_touch_down'),
                animate(label, x=0),
            )
            label.x = 0
            await or_(
                event(root, 'on_touch_down'),
                animate(label, y=0),
            )
            label.y = 0


if __name__ == '__main__':
    TestApp().run()
