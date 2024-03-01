import typing as T

from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
import asynckivy as ak

KV_CODE = '''
<YesNoDialog@ModalView>:
    size_hint: 0.8, 0.4
    BoxLayout:
        padding: '10dp'
        spacing: '10dp'
        orientation: 'vertical'
        Label:
            id: label
        BoxLayout:
            spacing: '10dp'
            Button:
                id: no_button
                text: 'No'
            Button:
                id: yes_button
                text: 'Yes'

Widget:
'''


async def ask_yes_no_question(question, *, _cache=[]) -> T.Awaitable[str]:
    dialog = _cache.pop() if _cache else F.YesNoDialog()
    no_button = dialog.ids.no_button
    yes_button = dialog.ids.yes_button

    dialog.ids.label.text = question
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(no_button, 'on_press'),
            ak.event(yes_button, 'on_press'),
        )
        for task, r in zip(tasks, ('CANCEL', 'NO', 'YES', )):
            if task.finished:
                break
        return r
    finally:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        self._main_task = ak.start(self.main())

    def on_stop(self):
        self._main_task.cancel()

    async def main(self):
        await ak.n_frames(2)

        msg = "Do you like Kivy?"
        res = await ask_yes_no_question(msg)
        print(f"{msg!r} --> {res}")

        await ak.sleep(.5)

        msg = "Do you like Python?"
        res = await ask_yes_no_question(msg)
        print(f"{msg!r} --> {res}")


if __name__ == '__main__':
    SampleApp().run()
