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
        ak.start(animate(self.root))


async def animate(root):
    from asynckivy import animate as a
    l = root.ids.label  # noqa: E741

    async def _blink_forever():
        while True:
            await a(l, color=(0, .3, 0, 1, ), t='out_quad')
            await a(l, color=(1, 1, 1, 1, ), t='in_quad')

    async def _round():
        await a(l, right=root.right)
        await a(l, top=root.top)
        await a(l, x=root.x)
        await a(l, y=root.y)
    ak.start(_blink_forever())
    while True:
        l.text = 'Hello'
        await _round()
        await a(l, center=root.center)
        l.pos_hint['center'] = (.5, .5, )
        await a(l, font_size=100.0, s=.1)
        l.pos_hint.clear()
        l.text = 'Kivy'
        await a(l, pos=root.pos)
        await _round()
        await a(l, font_size=60.0, s=.1)


if __name__ == '__main__':
    TestApp().run()
