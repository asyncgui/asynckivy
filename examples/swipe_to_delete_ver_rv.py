from kivy.lang import Builder

from swipe_to_delete import SampleApp as BaseApp


KV_CODE = r'''
BoxLayout:
    spacing: '10dp'
    padding: '10dp'
    orientation: 'vertical'
    Switch:
        id: switch
        active: False
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


class SampleApp(BaseApp):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp(title='Swipe to Delete (RecycleView)').run()
