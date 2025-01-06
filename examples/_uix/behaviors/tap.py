__all__ = ("KXTapGestureRecognizer", "KXMultiTapsGestureRecognizer", )

from collections.abc import Sequence
from functools import partial

from kivy.input.motionevent import MotionEvent
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import BooleanProperty, BoundedNumericProperty, NumericProperty
import asynckivy as ak


def _on_touch_down_filter(w, t):
    return w.collide_point(*t.opos) and (not t.is_mouse_scrolling)


class KXTapGestureRecognizer:
    is_being_pressed = BooleanProperty(False)

    def on_tap(self, touch: MotionEvent):
        '''
        :param touch: The ``MotionEvent`` instance that caused the ``on_tap`` event.
        '''

    def __init__(self, **kwargs):
        self.__main_task = ak.dummy_task
        self.register_event_type("on_tap")
        t = Clock.schedule_once(self._KXTapGestureRecognizer_reset)
        f = self.fbind
        f("disabled", t)
        f("parent", t)
        super().__init__(**kwargs)

    # Python's name mangling is weird. This method cannot be named '__reset'.
    def _KXTapGestureRecognizer_reset(self, __):
        self.__main_task.cancel()
        self.is_being_pressed = False
        self.__main_task = ak.start(self.__main())

    async def __main(self):
        if self.disabled:
            return
        with ak.suppress_event(self, "on_touch_down", filter=lambda w, t: w.collide_point(*t.opos)):
            touch = None
            on_touch_down = partial(ak.event, self, "on_touch_down", filter=_on_touch_down_filter)
            on_touch_up = partial(ak.event, Window, "on_touch_up", filter=lambda w, t: t is touch)
            to_parent = self.parent.to_widget
            while True:
                __, touch = await on_touch_down()
                self.is_being_pressed = True
                await on_touch_up()
                self.is_being_pressed = False
                # Because we received an on_touch_up event directly from the Window object, we need to manually
                # convert its coordinates.
                if self.collide_point(*to_parent(*touch.pos)):
                    self.dispatch("on_tap", touch)


class KXMultiTapsGestureRecognizer:
    is_being_pressed = BooleanProperty(False)
    max_taps = BoundedNumericProperty(2, min=1)
    max_tap_interval = NumericProperty(.3)

    def on_multi_taps(self, n_taps: int, touches: Sequence[MotionEvent]):
        ''''
        :param n_taps: This equals to ``len(touches)``.
        :param touches: The ``MotionEvent`` instances that caused the ``on_multi_taps`` event.
                        They are listed in the order they occurred.
        '''

    def __init__(self, **kwargs):
        self.__main_task = ak.dummy_task
        self.register_event_type("on_multi_taps")
        t = Clock.schedule_once(self._KXMultiTapsGestureRecognizer_reset)
        f = self.fbind
        f("disabled", t)
        f("parent", t)
        f("max_taps", t)
        f("max_tap_interval", t)
        super().__init__(**kwargs)

    # Python's name mangling is weird. This method cannot be named '__reset'.
    def _KXMultiTapsGestureRecognizer_reset(self, __):
        self.__main_task.cancel()
        self.is_being_pressed = False
        self.__main_task = ak.start(self.__main())

    async def __main(self):
        if self.disabled:
            return
        with ak.suppress_event(self, "on_touch_down", filter=lambda w, t: w.collide_point(*t.opos)):
            touch = None
            on_touch_down = partial(ak.event, self, "on_touch_down", filter=_on_touch_down_filter)
            on_touch_up = partial(ak.event, Window, "on_touch_up", filter=lambda w, t: t is touch)
            to_parent = self.parent.to_widget
            collide_point = self.collide_point
            timer = Timer(self.max_tap_interval)
            accepted_touches = []
            max_taps = self.max_taps
            while True:
                self.is_being_pressed = False
                accepted_touches.clear()
                n_taps = 0
                timer.stop()
                async with ak.move_on_when(timer.wait()):
                    while n_taps < max_taps:
                        __, touch = await on_touch_down()
                        self.is_being_pressed = True
                        timer.stop()
                        await on_touch_up()
                        self.is_being_pressed = False
                        # Because we received an on_touch_up event directly from the Window object, we need to
                        # manually convert its coordinates.
                        if collide_point(*to_parent(*touch.pos)):
                            n_taps += 1
                            accepted_touches.append(touch)
                            timer.start()
                        else:
                            break
                if n_taps:
                    self.dispatch("on_multi_taps", n_taps, accepted_touches)


class Timer:
    __slots__ = ("wait", "start", "stop")

    def __init__(self, timeout: float):
        event = ak.ExclusiveEvent()
        ce = Clock.create_trigger(event.fire, timeout, False, False)
        self.wait = event.wait
        self.start = ce
        self.stop = ce.cancel
