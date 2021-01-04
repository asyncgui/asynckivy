'''
Quiz Show
=========

A real-world example where ``aynckivy.or_()`` shines.
'''

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
import asynckivy as ak
from kivy.uix.screenmanager import NoTransition, Screen

KV_CODE = '''
<MyButton@Button>:
    font_size: sp(30)

<QuizScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: main_label
            font_size: sp(30)
        ProgressBar:
            id: time_bar
            size_hint_y: None
            height: 30
        RecycleView:
            id: choices
            viewclass: 'MyButton'
            size_hint_y: 3
            RecycleBoxLayout:
                default_size_hint: 1, 1
                default_size: None, None
                spacing: dp(20)
                padding: dp(20)
ScreenManager:
    id: scrmgr
    Screen:
        name: 'blank'
    Screen:
        name: 'title'
        MyButton:
            text: 'Start'
            size_hint: .5, .5
            pos_hint: {'center': (.5, .5, )}
            on_press: scrmgr.current = 'quiz'
    QuizScreen:
        name: 'quiz'
'''

quizzes = [
    {
        'question': '1 + 2 = ?',
        'choices': '0 1 2 3'.split(),
        'answer_idx': 3,
    },
    {
        'question': '123 * 456 = ?',
        'choices': '56088 57088 58088'.split(),
        'answer_idx': 0,
    },
]


class QuizScreen(Screen):
    def on_enter(self):
        self._main_coro = ak.start_soon(self._async_main())

    async def _async_main(self):
        ids = self.ids
        main_label = ids.main_label
        time_bar = ids.time_bar
        choices = ids.choices

        TIME_LIMIT = 5
        time_bar.max = TIME_LIMIT
        n_quizzes_shown = 0
        n_quizzes_beaten = 0
        for quiz in quizzes:
            n_quizzes_shown += 1
            async with ak.fade_transition(main_label, choices, d=.5):
                time_bar.value = TIME_LIMIT
                main_label.text = quiz['question']
                choices.data = \
                    ({'text': choice, } for choice in quiz['choices'])
            tasks = await ak.or_(
                *(
                    ak.event(child, 'on_press')
                    for child in reversed(choices.layout_manager.children)
                ),
                ak.animate(time_bar, value=0, d=TIME_LIMIT),
            )
            if tasks[-1].done:
                main_label.text = 'TIMEOUT!!'
            else:
                tasks[-1].cancel()
                if tasks[quiz['answer_idx']].done:
                    main_label.text = 'CORRECT'
                    n_quizzes_beaten += 1
                else:
                    main_label.text = 'INCORRECT'
            await ak.sleep(1)
        async with ak.fade_transition(main_label, choices, d=.5):
            main_label.text = \
                f"correct ratio {n_quizzes_beaten}/{n_quizzes_shown}"
            choices.data = []
            time_bar.value = 0
        await ak.sleep(2)
        async with ak.fade_transition(main_label, d=.5):
            main_label.text = "Thank you for playing"
        await ak.sleep(2)
        main_label.text = ''
        self.manager.current = 'title'


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        scrmgr = self.root
        scrmgr.transition = NoTransition()
        scrmgr.current = 'title'


if __name__ == '__main__':
    SampleApp().run()
