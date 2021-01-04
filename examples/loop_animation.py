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
        async def animate_label(label):
            sleep = asynckivy.sleep
            await sleep(0)
            await sleep(1)
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
        asynckivy.start(animate_label(self.root))


if __name__ == '__main__':
    TestApp().run()
