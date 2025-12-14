from collections import deque
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
import asynckivy as ak
from asynckivy import transition
from random import choice


KV_CODE = r'''
BoxLayout:
    orientation: 'vertical'
    RelativeLayout:
        id: screen_manager
        size_hint_y: 3
    AnchorLayout:
        padding: '20dp'
        Button:
            id: btn
            size_hint: None, None
            size: self.texture_size
            padding: '20dp'
            text: 'switch screen'
            font_size: '20sp'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        sm = self.root.ids.screen_manager
        btn = self.root.ids.btn
        screens = deque([
            F.Label(text='Screen 1', font_size=64),
            F.Button(text='Screen 2', font_size=64),
            F.Label(text='Screen 3', font_size=64),
            F.Button(text='Screen 4', font_size=64),
        ])
        transitions = [
            partial(transition.fade, duration=.5),
            partial(transition.slide, duration=.5, working_layer="outer"),
            partial(transition.scale, duration=.5, working_layer="outer"),
        ]
        current_screen = screens.popleft()
        sm.add_widget(current_screen)
        while True:
            await ak.event(btn, 'on_release')
            async with choice(transitions)(sm):
                sm.remove_widget(current_screen)
                screens.append(current_screen)
                current_screen = screens.popleft()
                sm.add_widget(current_screen)


if __name__ == '__main__':
    SampleApp().run()
