import asynckivy as ak


def _test():
    import textwrap
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.factory import Factory
    
    KV_CODE = textwrap.dedent('''
    <Label>:
        font_size: '24sp'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            id: label
            size_hint_y: None
            height: max(sp(24), self.texture_size[1])
        BoxLayout:
            id: layout
            spacing: 10
            Button:
                text: 'A'
            Button:
                text: 'B'
            Button:
                text: 'C'
    ''')
    
    class TestApp(App):
        def build(self):
            return Builder.load_string(KV_CODE)
        def on_start(self):
            import itertools
            import asynckivy as ak
            ids = self.root.ids
            label = ids.label
            buttons = list(reversed(ids.layout.children))
            async def test_await_multiple_coroutines():
                # -----------------------------------------
                # wait for the completion of one coroutine 
                # -----------------------------------------
                label.text = "wait until button'A' is pressed or 5s passes"
                tasks = await ak.or_(
                    ak.event(buttons[0], 'on_press'),
                    ak.sleep(5),
                )
                label.text = 'Done! ({})'.format(
                    "button'A' was pressed" if tasks[0].done else "5s passed"
                )
                await ak.sleep(1)
                label.text = 'next'
                await ak.sleep(1)

                # ------------------------------------------
                # wait for the completion of all coroutines
                # ------------------------------------------
                label.text = "wait until all buttons are pressed and 5s passes"
                tasks = await ak.and_(
                    ak.sleep(5),
                    *(ak.event(button, 'on_press') for button in buttons)
                )
                label.text = 'Done!'
                await ak.sleep(2)

            ak.start(test_await_multiple_coroutines())
            
    TestApp().run()


if __name__ == '__main__':
    _test()
    