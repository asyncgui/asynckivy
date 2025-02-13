from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak
from swipe_to_delete import enable_swipe_to_delete


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


def remove_corresponding_data(recyclelayout, view_widget):
    recyclelayout.recycleview.data.pop(recyclelayout.get_view_index_at(view_widget.center))


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        ids = self.root.ids
        switch = ids.switch
        container = ids.container
        while True:
            await ak.event(switch, 'active', filter=lambda _, active: active)
            async with ak.run_as_main(ak.event(switch, 'active')):
                await enable_swipe_to_delete(container, delete_action=remove_corresponding_data)


if __name__ == '__main__':
    SampleApp(title='Swipe to Delete (RecycleView)').run()
