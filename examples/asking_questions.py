import typing as T
import enum

from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
import asynckivy as ak

KV_CODE = '''
<MessageBox@ModalView>:
    size_hint: 0.8, 0.4
    BoxLayout:
        padding: '10dp'
        spacing: '10dp'
        orientation: 'vertical'
        Label:
            id: label
        Button:
            id: ok_button
            text: 'OK'

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

<InputDialog@ModalView>:
    size_hint: 0.8, 0.4
    BoxLayout:
        padding: '10dp'
        spacing: '10dp'
        orientation: 'vertical'
        Label:
            id: label
        TextInput:
            id: textinput
            multiline: False
        BoxLayout:
            spacing: '10dp'
            Button:
                id: cancel_button
                text: 'Cancel'
            Button:
                id: ok_button
                text: 'OK'

Widget:
'''


class CauseOfDismissal(enum.Enum):
    AUTO = enum.auto()  # ModalView.auto_dismiss or ModalView.dismiss()
    YES = enum.auto()
    NO = enum.auto()
    OK = enum.auto()
    CANCEL = enum.auto()
    UNKNOWN = enum.auto()  # potentially a bug


C = CauseOfDismissal


async def show_message_box(msg, *, _cache=[]) -> T.Awaitable[C]:
    dialog = _cache.pop() if _cache else F.MessageBox()
    label = dialog.ids.label
    ok_button = dialog.ids.ok_button

    label.text = msg
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(ok_button, 'on_press'),
        )
        for task, cause in zip(tasks, (C.AUTO, C.OK, )):
            if task.finished:
                return cause
        return C.UNKNOWN
    finally:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )


async def ask_yes_no_question(question, *, _cache=[]) -> T.Awaitable[C]:
    dialog = _cache.pop() if _cache else F.YesNoDialog()
    label = dialog.ids.label
    no_button = dialog.ids.no_button
    yes_button = dialog.ids.yes_button

    label.text = question
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(no_button, 'on_press'),
            ak.event(yes_button, 'on_press'),
        )
        for task, cause in zip(tasks, (C.AUTO, C.NO, C.YES, )):
            if task.finished:
                return cause
        return C.UNKNOWN
    finally:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )


async def ask_input(msg, *, input_filter, input_type, _cache=[]) -> T.Awaitable[T.Tuple[C, str]]:
    dialog = _cache.pop() if _cache else F.InputDialog()
    label = dialog.ids.label
    textinput = dialog.ids.textinput
    cancel_button = dialog.ids.cancel_button
    ok_button = dialog.ids.ok_button

    label.text = msg
    textinput.input_filter = input_filter
    textinput.input_type = input_type
    textinput.focus = True
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(cancel_button, 'on_press'),
            ak.event(ok_button, 'on_press'),
            ak.event(textinput, 'on_text_validate'),
        )
        for task, cause in zip(tasks, (C.AUTO, C.CANCEL, C.OK, C.OK, )):
            if task.finished:
                return cause, textinput.text
        return C.UNKNOWN, textinput.text
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
        ak.managed_start(self.main())

    async def main(self):
        await ak.n_frames(2)

        msg = "Do you like Kivy?"
        cause = await ask_yes_no_question(msg)
        print(f"{msg!r} --> {cause.name}")

        msg = "How long have you been using Kivy (in years) ?"
        while True:
            cause, years = await ask_input(msg, input_filter='int', input_type='number')
            if cause is C.OK:
                if years:
                    print(f"{msg!r} --> {years} years")
                    break
                else:
                    await show_message_box("The text box is empty. Try again.")
                    continue
            else:
                print(f"{msg!r} --> {cause.name}")
                break

        msg = "The armor I used to seal my all too powerful strength is now broken."
        cause = await show_message_box(msg)
        print(f"{msg!r} --> {cause.name}")


if __name__ == '__main__':
    SampleApp().run()
