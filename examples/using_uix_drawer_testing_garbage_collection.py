from kivy.app import runTouchApp
from kivy.lang import Builder
from asynckivy.uix.drawer import AKDrawer


class MyDrawer(AKDrawer):
    def on_kv_post(self, *args):
        from kivy.clock import Clock
        Clock.schedule_interval(self.report_aliveness, 1)
    def report_aliveness(self, *args):
        print("I'm still alive")


root = Builder.load_string(r'''
#:import gc gc

BoxLayout:
    orientation: 'vertical'
    FloatLayout:
        id: parent_of_drawer
        MyDrawer:
            id: drawer
            size_hint: None, None
            size: 200, 200
    Button:
        id: button_a
        text: 'remove the parent of drawer'
        size_hint_y: .1
        on_press:
            root.remove_widget(parent_of_drawer)
            gc.collect()
            button_a.disabled = True
            button_b.disabled = True
    Button:
        id: button_b
        text: 'remove drawer'
        size_hint_y: .1
        on_press:
            parent_of_drawer.remove_widget(drawer)
            gc.collect()
            button_a.disabled = True
            button_b.disabled = True
''')
runTouchApp(root)
