from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak

KV_CODE = r'''
FloatLayout:
    ScrollView:
        pos_hint: {"center_x": .5, "center_y": .5, }
        size_hint: None, None
        size: 200, 200
        canvas.before:
            Clear
        canvas.after:
            Clear
            Color:
            Line:
                rectangle: [*self.pos, *self.size]
                dash_offset: 5
                dash_length: 10
        Widget:
            id: target
            size_hint: 2, 2
            canvas:
                Color:
                    group: "color"
                Rectangle:
                    pos: self.pos
                    size: self.size
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        target = self.root.ids.target
        color = target.canvas.get_group("color")[0]
        color.a = .1

        while True:
            __, touch = await ak.event(target, "on_touch_down")
            was_inside = target.collide_point(*touch.pos)
            color.a = .5 if was_inside else .1

            async with ak.visibility_aware_touch_events(target, touch) as on_touch_move:
                while True:
                    is_inside = await on_touch_move()
                    if was_inside is is_inside:
                        pass
                    else:
                        color.a = .5 if is_inside else .1
                        was_inside = is_inside
            color.a = .1


if __name__ == "__main__":
    SampleApp(title="Visibility-Aware Touch Events").run()
