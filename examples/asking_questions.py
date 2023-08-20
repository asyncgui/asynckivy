import typing as T
import enum

from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
import asynckivy as ak

KV_CODE = '''
<MessageBox@ModalView>:
    BoxLayout:
        padding: '10dp'
        spacing: '10dp'
        orientation: 'vertical'
        Label:
            id: label
        Button:
            id: ok_button

<YesNoDialog@ModalView>:
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
            Button:
                id: yes_button

<InputDialog@ModalView>:
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


class DialogResponse(enum.Enum):
    YES = enum.auto()
    NO = enum.auto()
    OK = enum.auto()
    CANCEL = enum.auto()


R = DialogResponse


async def show_message_box(
        msg, *, ok_text='OK', size_hint=(0.8, 0.4, ),
        auto_dismiss=F.ModalView.auto_dismiss.defaultvalue,
        _cache=[]) -> T.Awaitable[R]:
    try:
        dialog = _cache.pop()
    except IndexError:
        dialog = F.MessageBox()

    label = dialog.ids.label
    ok_button = dialog.ids.ok_button

    dialog.size_hint = size_hint
    dialog.auto_dismiss = auto_dismiss
    label.text = msg
    ok_button.text = ok_text
    try:
        dialog.open()
        tasks = await ak.wait_any(
            ak.event(dialog, 'on_pre_dismiss'),
            ak.event(ok_button, 'on_press'),
        )
        for task, r in zip(tasks, (R.CANCEL, R.OK, )):
            if task.finished:
                break
        dialog.dismiss()
        await ak.sleep(dialog._anim_duration + 0.1)
        _cache.append(dialog)
        return r
    except ak.Cancelled:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )
        raise


async def ask_yes_no_question(
        question, *, yes_text='Yes', no_text='No', size_hint=(0.8, 0.4, ),
        auto_dismiss=F.ModalView.auto_dismiss.defaultvalue,
        _cache=[]) -> T.Awaitable[R]:
    try:
        dialog = _cache.pop()
    except IndexError:
        dialog = F.YesNoDialog()

    label = dialog.ids.label
    no_button = dialog.ids.no_button
    yes_button = dialog.ids.yes_button

    dialog.size_hint = size_hint
    dialog.auto_dismiss = auto_dismiss
    label.text = question
    no_button.text = no_text
    yes_button.text = yes_text
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
        dialog.dismiss()
        await ak.sleep(dialog._anim_duration + 0.1)
        _cache.append(dialog)
        return r
    except ak.Cancelled:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )
        raise


async def ask_input(
        msg, *, ok_text='OK', cancel_text='Cancel', size_hint=(0.8, 0.4, ),
        auto_dismiss=F.ModalView.auto_dismiss.defaultvalue,
        input_filter=F.TextInput.input_filter.defaultvalue,
        input_type=F.TextInput.input_type.defaultvalue,
        _cache=[]) -> T.Awaitable[T.Tuple[R, str]]:
    try:
        dialog = _cache.pop()
    except IndexError:
        dialog = F.InputDialog()

    label = dialog.ids.label
    textinput = dialog.ids.textinput
    cancel_button = dialog.ids.cancel_button
    ok_button = dialog.ids.ok_button

    dialog.size_hint = size_hint
    dialog.auto_dismiss = auto_dismiss
    label.text = msg
    cancel_button.text = cancel_text
    ok_button.text = ok_text
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
        for task, r in zip(tasks, (R.CANCEL, R.CANCEL, R.OK, R.OK, )):
            if task.finished:
                break
        dialog.dismiss()
        await ak.sleep(dialog._anim_duration + 0.1)
        _cache.append(dialog)
        return r, textinput.text
    except ak.Cancelled:
        dialog.dismiss()
        Clock.schedule_once(
            lambda dt: _cache.append(dialog),
            dialog._anim_duration + 0.1,
        )
        raise


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
        print(f"{msg!r} --> {res.name}")

        msg = "How long have you been using Kivy (in years) ?"
        while True:
            res, years = await ask_input(msg, input_filter='int', input_type='number')
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
        res = await show_message_box(msg)
        print(f"{msg!r} --> {res.name}")


if __name__ == '__main__':
    SampleApp().run()
