from contextlib import asynccontextmanager

import requests

from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
import asynckivy as ak

from progress_spinner import progress_spinner

KV_CODE = '''
<LoadingDialog@ModalView>:
    size_hint: 0.8, 0.8
    BoxLayout:
        padding: '20dp'
        spacing: '20dp'
        orientation: 'vertical'
        Label:
            id: label
            font_size: '20sp'
            size_hint_y: 3
        Button:
            id: button
            font_size: '20sp'
            size_hint_x: .4
            pos_hint: {'center_x': .5, }

FloatLayout:
    Button:
        id: open_button
        text: 'open dialog'
        font_size: '20sp'
        size_hint: .3, .1
        pos_hint: {'center_x': .5, 'center_y': .5}
        on_release: root_nursery.start(app.demonstrate_dialog())
'''


@asynccontextmanager
async def open_dialog(*, _cache=[]):
    dialog = _cache.pop() if _cache else F.LoadingDialog()
    dialog.auto_dismiss = False
    dialog.ids.label.text = ''
    dialog.ids.button.text = ''
    dialog.open()
    try:
        await ak.sleep(dialog._anim_duration + 0.1)
        dialog.auto_dismiss = True
        yield dialog
    finally:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )


class SampleApp(App):
    def build(self):
        self._main_task = ak.start(self.main())
        return Builder.load_string(KV_CODE)

    def on_stop(self):
        self._main_task.cancel()

    async def main(self):
        from kivy.lang import global_idmap
        async with ak.open_nursery() as nursery:
            global_idmap['root_nursery'] = nursery
            await ak.sleep_forever()

    async def demonstrate_dialog(self):
        # The 'auto_dismiss_tracker' would be unnecessary if the 'dialog.auto_dismiss' was set to False
        async with open_dialog() as dialog, ak.wait_any_cm(ak.event(dialog, 'on_pre_dismiss')) as auto_dismiss_tracker:
            label = dialog.ids.label
            button = dialog.ids.button

            label.text = 'Press the button to start HTTP requests'
            button.text = 'Start'
            await ak.event(button, 'on_press')
            button.text = 'Cancel'
            session = requests.Session()
            url = "https://httpbin.org/delay/2"

            async with ak.run_as_daemon(progress_spinner(
                draw_target=dialog.canvas,
                center=label.center,
                radius=min(label.size) * 0.4,
                color=(1, 1, 1, .3),
            )):
                async with ak.wait_any_cm(ak.event(button, 'on_press')) as cancel_tracker:
                    async with ak.run_as_primary(ak.run_in_thread(lambda: session.get(url), daemon=True)):
                        async with ak.fade_transition(label, duration=.6):
                            label.text = 'First request...'
                    async with ak.run_as_primary(ak.run_in_thread(lambda: session.get(url), daemon=True)):
                        async with ak.fade_transition(label, duration=.6):
                            label.text = 'Second request...'

            async with ak.fade_transition(label, button, duration=.6):
                label.text = 'Cancelled' if cancel_tracker.finished else 'All requests are done'
                button.text = 'OK'
            await ak.event(button, 'on_press')

        if auto_dismiss_tracker.finished:
            print("Dialog was auto-dismissed")


if __name__ == '__main__':
    SampleApp().run()
