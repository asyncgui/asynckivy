import itertools

from kivy.app import App
from kivy.lang import Builder

import asynckivy as ak
from asynckivy.transition import slide_transition

KV_CODE = r'''
AnchorLayout:
    Label:
        id: label
        font_size: '200sp'
        size_hint: .5, .5
        canvas.before:
            Color:
            Line:
                rectangle: [*self.pos, *self.size, ]
                dash_offset: 4
                dash_length: 4
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        await ak.n_frames(2)
        label = self.root.ids.label.__self__
        with ak.stencil_widget_mask(label, use_outer_canvas=True):
            for text in itertools.cycle('ABC'):
                async with slide_transition(label, out_curve='in_back', in_curve='out_back'):
                    label.text = text
                await ak.sleep(1)


if __name__ == '__main__':
    SampleApp(title="Stencil Mask").run()
