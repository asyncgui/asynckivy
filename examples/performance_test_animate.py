from kivy.config import Config
Config.set('graphics', 'maxfps', 0)
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak


KV_CODE = '''
BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    ToggleButton:
        text: 'simple ver.'
        group: 'aaa'
        on_press:
            app.reset()
            if self.state == 'down': app.start_anim(ver='simple')
    ToggleButton:
        text: 'complex ver.'
        group: 'aaa'
        on_press:
            app.reset()
            if self.state == 'down': app.start_anim(ver='complex')
'''


class AnimTarget:
    value = 0.


class SampleApp(App):
    coro = None

    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        def print_fps(dt):
            print(Clock.get_fps(), 'fps')
        Clock.schedule_interval(print_fps, 2)

    def reset(self):
        coro = self.coro
        if coro is not None:
            coro.close()
        self.coro = None

    def start_anim(self, ver):
        self.coro = self._anim(ver)
        ak.start(self.coro)

    async def _anim(self, ver):
        from importlib import import_module
        animate = import_module(f"asynckivy._animation._{ver}_ver").animate
        target = AnimTarget()
        print(f'---- start {ver} version ----')
        while True:
            await animate(target, value=100., d=10.)
            await animate(target, value=0., d=10.)


if __name__ == '__main__':
    SampleApp().run()
