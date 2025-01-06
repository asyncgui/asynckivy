from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.app import App


from _uix.behaviors.tap import KXTapGestureRecognizer, KXMultiTapsGestureRecognizer


class MultiTapButton(KXMultiTapsGestureRecognizer, Label):
    def on_multi_taps(self, n_taps, touches):
        if n_taps == 1:
            print("single-tapped.")
        elif n_taps == 2:
            print("double-tapped.")
        else:
            print(f"{n_taps}-tapped.")


class SingleTapButton(KXTapGestureRecognizer, Label):
    def on_tap(self, touch):
        print("tapped.")


KV_CODE = '''
#:set YELLOW rgba("#FFFF00")

<MultiTapButton, SingleTapButton>:
    canvas:
        Color:
            rgba: self.disabled_color if self.disabled else (YELLOW if self.is_being_pressed else self.color)
        Line:
            width: dp(3)
            rectangle: (*self.pos, *self.size, )

BoxLayout:
    padding: 40, 40
    spacing: 40
    orientation: 'vertical'
    RelativeLayout:  # This is only to test if the coordinates are converted correctly.
        MultiTapButton:
            font_size: 30
            text: "This recognizes multi-tap gestures."
            disabled: not switch.active
            max_taps: 7
    RelativeLayout:  # This is only to test if the coordinates are converted correctly.
        SingleTapButton:
            font_size: 30
            text: "This one doesn't."
            disabled: not switch.active
    Switch:
        id: switch
        active: True
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp(title='multi-tap').run()
