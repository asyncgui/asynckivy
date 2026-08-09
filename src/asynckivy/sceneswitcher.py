from collections.abc import Callable, AsyncGenerator, Awaitable, Coroutine
from typing import TypeAlias, Any
from inspect import isasyncgen
from importlib import import_module

from kivy.uix.widget import Widget

UserData: TypeAlias = Any
Scene: TypeAlias = Callable[[Widget, UserData], AsyncGenerator]


def _import_scene(absolute_name: str) -> Scene:
    module_name, scene_name = absolute_name.rsplit(".", 1)
    return getattr(import_module(module_name), scene_name)

def _yield_prohibited_await(coro: Coroutine):
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    else:
        raise RuntimeError("一時停止してはいけない箇所で停止しました")
    

# async def pseudo_scene_example(parent: Widget, userdata: UserData):
#     # set up
#     yield
#     # run the scene
#     yield next_scene, how_to_transition
#     # tear down


async def run(first_scene: Scene | str, *, parent: Widget=None, userdata: UserData=None):
    if parent is None:
        from kivy.app import App
        parent = App.get_running_app().root

    if isinstance(first_scene, str):
        first_scene = _import_scene(first_scene)

    cur_scene = first_scene
    cur_agen = cur_scene(parent, userdata)
    if not isasyncgen(cur_agen):
        raise TypeError(f"{cur_scene} didn't return an async generator")

    while True:
        

    r = _yield_prohibited_await(cur_agen.asend(None))
    if r is not None:
        raise RuntimeError(f"The first value yielded must be None, but got {r}.")
