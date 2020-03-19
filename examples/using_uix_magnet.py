from kivy.app import runTouchApp
from kivy.lang import Builder

root = Builder.load_string(r'''
#:import Image kivy.uix.image.Image
#:import AKMagnet asynckivy.uix.magnet.AKMagnet
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        spacing: 20
        GridLayout:
            cols: 4
            id: left_pane
        GridLayout:
            rows: 4
            id: right_pane
    GridLayout:
        size_hint_y: .2
        rows: 2
        cols: 2
        Button:
            disabled: len(left_pane.children) == 0
            text: 'move a widget from left to right'
            on_press:
                child = left_pane.children[-1]
                left_pane.remove_widget(child)
                right_pane.add_widget(child)
        Button:
            disabled: len(right_pane.children) == 0
            text: 'move a widget from right to left'
            on_press:
                child = right_pane.children[-1]
                right_pane.remove_widget(child)
                left_pane.add_widget(child)
        Button:
            text: 'add a widget to the left side'
            on_press:
                magnet = AKMagnet()
                magnet.add_widget(Image(source='data/logo/kivy-icon-256.png'))
                left_pane.add_widget(magnet)
        Button:
            text: 'add a widget to the right side'
            on_press:
                magnet = AKMagnet()
                magnet.add_widget(Image(source='data/logo/kivy-icon-256.png', color=(1, 1, 0, 1, )))
                right_pane.add_widget(magnet)
''')
runTouchApp(root)
