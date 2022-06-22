'''
A little bit complex loop-animation.
'''

from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak


KV_CODE = r'''
FloatLayout:
    Label:
        id: label
        font_size: 60.0
        size_hint: None, None
        size: self.texture_size
'''


class TestApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.start(self.main())

    async def main(self):
        from asynckivy import animate
        root = self.root
        label = root.ids.label
        round = self._round

        ak.start(self._blink_forever(label))
        while True:
            label.text = 'Hello'
            await round(root, label)
            await animate(label, center=root.center)
            label.pos_hint['center'] = (.5, .5, )
            await animate(label, font_size=100.0, s=.1)
            del label.pos_hint['center']
            label.text = 'Kivy'
            await animate(label, pos=root.pos)
            await round(root, label)
            await animate(label, font_size=60.0, s=.1)

    @staticmethod
    async def _blink_forever(label):
        from asynckivy import animate
        while True:
            await animate(label, color=(0, .3, 0, 1, ), t='out_quad')
            await animate(label, color=(1, 1, 1, 1, ), t='in_quad')

    @staticmethod
    async def _round(parent, widget):
        from asynckivy import animate
        await animate(widget, right=parent.right)
        await animate(widget, top=parent.top)
        await animate(widget, x=parent.x)
        await animate(widget, y=parent.y)


if __name__ == '__main__':
    TestApp().run()
