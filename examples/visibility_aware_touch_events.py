from kivy.app import App
from kivy.lang import Builder
import asynckivy as ak

KV_CODE = r'''
FloatLayout:
    FloatLayout:
        id: clipper
        pos_hint: {"x": .2, "y": .2, }
        size_hint: .4, .4
        canvas.after:
            Color:
            Line:
                rectangle: [*self.pos, *self.size]
                dash_offset: 5
                dash_length: 10
        Widget:
            id: target
            pos_hint: {"x": .5, "y": .5, }
            canvas:
                Color:
                    group: "color"
                Rectangle:
                    pos: self.pos
                    size: self.size
'''


def block_outside_ones(w, t):
    return not w.collide_point(*t.pos)


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        self.root.ids.clipper.bind(
            on_touch_down=block_outside_ones,
            on_touch_move=block_outside_ones,
            on_touch_up=block_outside_ones,
        )

        target = self.root.ids.target.__self__
        color = target.canvas.get_group("color")[0]
        color.a = .1

        while True:
            # Not a recommended way to use `wait_any`, but for the simplicity of the code.
            tasks = await ak.wait_any(
                ak.event(target, "on_touch_down"),
                ak.event(target, "on_touch_move"),
            )
            touch = (tasks[0].result if tasks[0].finished else tasks[1].result)[1]
            was_inside = target.collide_point(*target.parent.to_widget(*touch.pos))
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
