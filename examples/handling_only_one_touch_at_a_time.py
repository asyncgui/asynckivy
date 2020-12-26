from kivy.app import runTouchApp
import asynckivy as ak

try:
    from .handling_multiple_touches_at_a_time import Painter as OriginalPainter
except ImportError:
    from handling_multiple_touches_at_a_time import Painter as OriginalPainter


class Painter(OriginalPainter):
    def on_touch_down(self, touch):
        pass

    def on_kv_post(self, *args, **kwargs):
        ak.start(self.keep_watching_touch_events())

    async def keep_watching_touch_events(self):
        while True:
            __, touch = await ak.event(
                self, 'on_touch_down',
                filter=lambda w, t: w.collide_point(*t.opos),
                return_value=True,
            )
            await self.draw_rect(touch)


if __name__ == "__main__":
    runTouchApp(Painter())
