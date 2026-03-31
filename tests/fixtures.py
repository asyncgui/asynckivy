from functools import partial
from dataclasses import dataclass
import pytest


from kivy.context import Context
from kivy.factory import FactoryBase, Factory
from kivy.lang import BuilderBase, Builder
from kivy.clock import ClockBase, Clock
from kivy.base import EventLoopBase, EventLoop


@dataclass(kw_only=True, slots=True)
class KivyRunner:
    builder: BuilderBase = Builder
    factory: FactoryBase = Factory
    clock: ClockBase = Clock
    eventloop: EventLoopBase = EventLoop
    window: object = None
    current_time: float = 0.0

    def advance_a_frame(self, *, dt=0.1) -> None:
        self.current_time += dt
        self.eventloop.idle()


@pytest.fixture()
def kivy_runner():
    from kivy.core.window import EventLoop, Window, stopTouchApp

    def clear_window_and_event_loop():
        for child in Window.children[:]:
            Window.remove_widget(child)
        Window.canvas.before.clear()
        Window.canvas.clear()
        Window.canvas.after.clear()
        EventLoop.touches.clear()
        for post_proc in EventLoop.postproc_modules:
            if hasattr(post_proc, "touches"):
                post_proc.touches.clear()
            elif hasattr(post_proc, "last_touches"):
                post_proc.last_touches.clear()

    from os import environ

    environ["KIVY_USE_DEFAULTCONFIG"] = "1"

    # force window size + remove all inputs
    from kivy.config import Config

    Config.set("graphics", "width", "320")
    Config.set("graphics", "height", "240")
    for items in Config.items("input"):
        Config.remove_option("input", items[0])

    context = Context(init=False)
    context["Clock"] = clock = ClockBase()
    clock._max_fps = 0
    clock.start_clock()
    context.push()
    runner = KivyRunner(window=Window, current_time=clock.time())
    clock.time = partial(getattr, runner, "current_time")

    # ensure our window is correctly created
    Window.create_window()
    Window.register()
    Window.initialized = True
    Window.close = lambda *s: None
    clear_window_and_event_loop()

    yield runner
    clock.stop_clock()
    if EventLoop.status == "started":
        clear_window_and_event_loop()
        stopTouchApp()
    context.pop()


@pytest.fixture()
def isolate_builder_and_factory():
    context = Context(init=False)
    context["Factory"] = FactoryBase.create_from(Factory)
    context["Builder"] = BuilderBase.create_from(Builder)
    context.push()

    try:
        yield
    finally:
        context.pop()
