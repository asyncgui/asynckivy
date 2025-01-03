__all__ = ("KXTapGestureRecognizer", )

from functools import partial
from kivy.clock import Clock
import asynckivy as ak


def _on_touch_down_filter(w, t):
    return w.collide_point(*t.opos) and (not t.is_mouse_scrolling)


class KXTapGestureRecognizer:
    def __init__(self, **kwargs):
        self.__main_task = ak.dummy_task
        self.register_event_type("on_tap")
        trigger_reset = Clock.schedule_once(self._KXTapGestureRecognizer_reset)
        self.fbind("disabled", trigger_reset)
        super().__init__(**kwargs)

    # Python's name mangling is weird. I can't name this method '__reset'.
    def _KXTapGestureRecognizer_reset(self, __):
        self.__main_task.cancel()
        self.__main_task = ak.start(self.__main())

    async def __main(self):
        if self.disabled:
            return
        se = partial(ak.suppress_event, self, filter=lambda w, t: w.collide_point(*t.pos))
        with se("on_touch_down"), se("on_touch_move"), se("on_touch_up"):
            touch = None
            on_touch_down = partial(ak.event, self, "on_touch_down", filter=_on_touch_down_filter)
            on_touch_up = partial(ak.event, self, "on_touch_up", filter=lambda w, t: t is touch)
            while True:
                __, touch = await on_touch_down()
                await on_touch_up()
                if self.collide_point(*touch.pos):
                    self.dispatch("on_tap", touch)

    def on_tap(self, touch):
        pass
