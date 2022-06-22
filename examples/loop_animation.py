'''
A simple loop-animation.
'''

from kivy.app import App
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
import asynckivy


class TestApp(App):

    def build(self):
        return Label(text='Hello', markup=True, font_size='80sp',
                     outline_width=2,
                     outline_color=get_color_from_hex('#FFFFFF'),
                     color=get_color_from_hex('#000000'),
                     )

    def on_start(self):
        asynckivy.start(self.main())

    async def main(self):
        label = self.root
        sleep = asynckivy.sleep
        await asynckivy.n_frames(4)
        while True:
            label.outline_color = get_color_from_hex('#FFFFFF')
            label.text = 'Do'
            await sleep(.5)
            label.text = 'you'
            await sleep(.5)
            label.text = 'like'
            await sleep(.5)
            label.text = 'Kivy?'
            await sleep(2)

            label.outline_color = get_color_from_hex('#FF5555')
            label.text = 'Answer me!'
            await sleep(2)


if __name__ == '__main__':
    TestApp().run()
