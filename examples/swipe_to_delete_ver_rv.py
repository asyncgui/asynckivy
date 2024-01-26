from kivy.app import App
from kivy.lang import Builder


KV_CODE = r'''
#:import ak asynckivy
#:import swipe_to_delete swipe_to_delete.swipe_to_delete

BoxLayout:
    spacing: '10dp'
    padding: '10dp'
    orientation: 'vertical'
    Switch:
        active: False
        on_active:
            (
            setattr(container, '_swipe_to_delete_task', ak.start(swipe_to_delete(container)))
            if args[1] else
            container._swipe_to_delete_task.cancel()
            )
        size_hint_y: None
        height: '50dp'
    RecycleView:
        data: [{'text': str(i), } for i in range(100)]
        viewclass: 'Button'
        RecycleBoxLayout:
            id: container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: '10dp'
            default_size_hint: 1, None
            default_height: '50dp'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp(title='Swipe to Delete (RecycleView)').run()
