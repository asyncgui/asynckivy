from typing import Literal
from collections.abc import Awaitable

from kivy.core.window import Window, WindowBase
from kivy.lang import Builder
from kivy.factory import Factory


import asynckivy as ak
from asynckivy import modal


Builder.load_string('''
<YesNoDialog@BoxLayout>:
    padding: '20dp'
    spacing: '20dp'
    orientation: 'vertical'
    size_hint: .5, .5
    size_hint_min: self.minimum_size
    pos_hint: {'center_x': .5, 'center_y': .5}
    canvas.before:
        Color:
        Line:
            width: dp(2)
            rectangle: (*self.pos, *self.size, )
    Label:
        id: question
        size_hint_min: self.texture_size
    BoxLayout:
        spacing: '10dp'
        size_hint_min: self.minimum_size
        Button:
            id: no_button
            size_hint_min: self.texture_size
        Button:
            id: yes_button
            size_hint_min: self.texture_size
''')
YesNoDialog = Factory.YesNoDialog


async def ask_yes_no_question(
    question: str, *, window: WindowBase=Window, yes_text='Yes', no_text='No',
    transition=modal.FadeTransition(), auto_dismiss=True, _cache=[],
) -> Awaitable[Literal['yes', 'no', None]]:
    '''
    Asks the user a yes/no question via a modal dialog.

    .. code-block::

        answer = await ask_yes_no_question("Do you like Kivy?")

    :return: None if the dialog is auto-dismissed.
    '''
    dialog = _cache.pop() if _cache else YesNoDialog()
    try:
        ids = dialog.ids
        ids.question.text = question
        ids.yes_button.text = yes_text
        ids.no_button.text = no_text
        async with modal.open(dialog, window=window, auto_dismiss=auto_dismiss, transition=transition) as ad_event:
            tasks = await ak.wait_any(
                ak.event(ids.yes_button, 'on_release'),
                ak.event(ids.no_button, 'on_release'),
            )
        if ad_event.is_fired:
            return None
        return 'yes' if tasks[0].finished else 'no'
    finally:
        _cache.append(dialog)


def main():
    from textwrap import dedent
    from kivy.lang import Builder
    from kivy.app import App

    class TestApp(App):
        def build(self):
            return Builder.load_string(dedent('''
                #:import ak asynckivy

                <Label>:
                    font_size: '24sp'

                AnchorLayout:
                    Button:
                        id: button
                        size_hint: .4, .2
                        size_hint_min: self.texture_size
                        padding: '10dp'
                        text: "start answering questions"
                        on_release: ak.managed_start(app.ask_questions())
                '''))

        async def ask_questions(self):
            questions = [
                "Do you like Python?",
                "Do you like Kivy?",
                "Do you like AsyncKivy?",
            ]
            for q in questions:
                answer = await ask_yes_no_question(q)
                if answer is None:
                    answer = '<no answer>'
                print(q, '->', answer)
    TestApp().run()


if __name__ == '__main__':
    main()
