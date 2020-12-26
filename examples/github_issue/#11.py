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
        async def some_task():
            label = self.root.ids.label
            button = self.root.ids.button
            label.text = '--'
            button.text = 'start spinning'
            await ak.event(button, 'on_press')
            button.text = 'stop'
            tasks = await ak.or_(
                ak.event(button, 'on_press'),
                spinning(label),
            )
            tasks[1].cancel()
            self.root.remove_widget(button)
            label.text = 'fin.'
        ak.start(some_task())


async def spinning(label):
    import itertools
    sleep_for_10th_of_a_second = await ak.create_sleep(.1)
    for stick in itertools.cycle(r'\ | / --'.split()):
        label.text = stick
        await sleep_for_10th_of_a_second()


if __name__ == '__main__':
    TestApp().run()
