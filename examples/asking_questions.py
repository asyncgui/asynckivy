import typing as T
import enum
from dataclasses import dataclass

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.uix.modalview import ModalView
import asynckivy as ak

KV_CODE = '''
<MessageBox>:
    size_hint: root.theme.size_hint
    auto_dismiss: root.theme.auto_dismiss
    BoxLayout:
        padding: '10dp'
        spacing: '10dp'
        orientation: 'vertical'
        Label:
            id: label
            font_size: root.theme.font_size
            font_name: root.theme.font_name
        Button:
            id: ok_button
            font_size: root.theme.font_size
            font_name: root.theme.font_name
            text: root.theme.text_ok

<YesNoDialog>:
    size_hint: root.theme.size_hint
    auto_dismiss: root.theme.auto_dismiss
    BoxLayout:
        padding: '10dp'
        spacing: '10dp'
        orientation: 'vertical'
        Label:
            id: label
            font_size: root.theme.font_size
            font_name: root.theme.font_name
        BoxLayout:
            spacing: '10dp'
            Button:
                id: no_button
                font_size: root.theme.font_size
                font_name: root.theme.font_name
                text: root.theme.text_no
            Button:
                id: yes_button
                font_size: root.theme.font_size
                font_name: root.theme.font_name
                text: root.theme.text_yes

<InputDialog>:
    size_hint: root.theme.size_hint
    auto_dismiss: root.theme.auto_dismiss
    BoxLayout:
        padding: '10dp'
        spacing: '10dp'
        orientation: 'vertical'
        Label:
            id: label
            font_size: root.theme.font_size
            font_name: root.theme.font_name
        TextInput:
            id: textinput
            multiline: False
            font_size: root.theme.font_size
        BoxLayout:
            spacing: '10dp'
            Button:
                id: cancel_button
                font_size: root.theme.font_size
                font_name: root.theme.font_name
                text: root.theme.text_cancel
            Button:
                id: ok_button
                font_size: root.theme.font_size
                font_name: root.theme.font_name
                text: root.theme.text_ok

Widget:
'''


@dataclass
class DialogTheme:
    size_hint: tuple = (0.8, 0.4, )
    auto_dismiss: bool = ModalView.auto_dismiss.defaultvalue
    font_size: int = F.Label.font_size.defaultvalue
    font_name: int = F.Label.font_name.defaultvalue
    text_yes: str = 'Yes'
    text_no: str = 'No'
    text_ok: str = 'OK'
    text_cancel: str = 'Cancel'


default_theme = DialogTheme()


class DialogResponse(enum.Enum):
    YES = enum.auto()
    NO = enum.auto()
    OK = enum.auto()
    CANCEL = enum.auto()


R = DialogResponse


class MessageBox(ModalView):
    theme = ObjectProperty(default_theme, rebind=True)


class YesNoDialog(ModalView):
    theme = ObjectProperty(default_theme, rebind=True)


class InputDialog(ModalView):
    theme = ObjectProperty(default_theme, rebind=True)


async def show_message_box(msg, *, theme=default_theme, _cache=[]) -> T.Awaitable[R]:
    dialog = _cache.pop() if _cache else MessageBox()
    label = dialog.ids.label
    ok_button = dialog.ids.ok_button

    dialog.theme = theme
    label.text = msg
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(ok_button, 'on_press'),
        )
        for task, r in zip(tasks, (R.CANCEL, R.OK, )):
            if task.finished:
                break
        return r
    finally:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )


async def ask_yes_no_question(question, *, theme=default_theme, _cache=[]) -> T.Awaitable[R]:
    dialog = _cache.pop() if _cache else YesNoDialog()
    label = dialog.ids.label
    no_button = dialog.ids.no_button
    yes_button = dialog.ids.yes_button

    dialog.theme = theme
    label.text = question
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(no_button, 'on_press'),
            ak.event(yes_button, 'on_press'),
        )
        for task, r in zip(tasks, (R.CANCEL, R.NO, R.YES, )):
            if task.finished:
                break
        return r
    finally:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )


async def ask_input(msg, *, input_filter, input_type, theme=default_theme, _cache=[]) -> T.Awaitable[T.Tuple[R, str]]:
    dialog = _cache.pop() if _cache else InputDialog()
    label = dialog.ids.label
    textinput = dialog.ids.textinput
    cancel_button = dialog.ids.cancel_button
    ok_button = dialog.ids.ok_button

    dialog.theme = theme
    label.text = msg
    textinput.focus = True
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(cancel_button, 'on_press'),
            ak.event(ok_button, 'on_press'),
            ak.event(textinput, 'on_text_validate'),
        )
        for task, r in zip(tasks, (R.CANCEL, R.CANCEL, R.OK, R.OK, )):
            if task.finished:
                break
        return r, textinput.text
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

        theme = DialogTheme(font_size='20sp')

        msg = "Do you like Kivy?"
        res = await ask_yes_no_question(msg, theme=theme)
        print(f"{msg!r} --> {res.name}")

        msg = "How long have you been using Kivy (in years) ?"
        while True:
            res, years = await ask_input(msg, input_filter='int', input_type='number', theme=theme)
            if res is R.OK:
                if years:
                    print(f"{msg!r} --> {years} years")
                    break
                else:
                    await show_message_box("The text box is empty. Try again.")
                    continue
            else:
                print(f"{msg!r} --> {res.name}")
                break

        msg = "The armor I used to seal my all too powerful strength is now broken."
        res = await show_message_box(msg, theme=theme)
        print(f"{msg!r} --> {res.name}")


if __name__ == '__main__':
    SampleApp().run()
