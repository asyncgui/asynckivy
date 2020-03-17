from kivy.config import Config
Config.set('graphics', 'maxfps', 0)
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.app import runTouchApp
import asynckivy as ak


class AnimTarget:
    value = 0.

root = Factory.BoxLayout(padding=10, spacing=10)
coro = None
def on_press(b):
    from importlib import import_module
    global coro
    if coro is not None:
        coro.close()
    if b.state == 'down':
        async def anim():
            target = AnimTarget()
            animate = import_module(f"asynckivy._animation._{b.text}").animate
            while True:
                await animate(target, value=100., d=10.)
                await animate(target, value=0., d=10.)
        coro = anim()
        print(f'start {b.text}')
        ak.start(coro)
    else:
        print(f'end {b.text}')

for text in ('simple_ver', 'complex_ver', ):
    root.add_widget(Factory.ToggleButton(
        group='anim_ver',
        text=text,
        on_press=on_press,
    ))

def print_fps(dt):
    print(Clock.get_fps(), 'fps')
Clock.schedule_interval(print_fps, 2)

runTouchApp(root)
