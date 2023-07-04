from kivy.lang import Builder
from kivy.app import App
import asynckivy as ak


KV_CODE = '''
BoxLayout:
    orientation: 'vertical'
    Label:
        id: label
        font_size: 50
    Button:
        id: button
        font_size: 50
'''


class TestApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.start(self.main())

    async def main(self):
        label = self.root.ids.label
        button = self.root.ids.button
        label.text = '--'
        button.text = 'start spinning'
        await ak.event(button, 'on_press')
        button.text = 'stop'
        tasks = await ak.wait_any(
            ak.event(button, 'on_press'),
            spinning(label),
        )
        tasks[1].cancel()
        self.root.remove_widget(button)
        label.text = 'fin.'


async def spinning(label):
    import itertools
    for stick in itertools.cycle(r'\ | / --'.split()):
        label.text = stick
        await ak.sleep(.1)


if __name__ == '__main__':
    TestApp().run()
