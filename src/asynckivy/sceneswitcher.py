from collections.abc import Callable, AsyncGenerator, Coroutine
from typing import TypeAlias, Any
from inspect import isasyncgen
from importlib import import_module
import contextlib

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
#     with ExitStack() as stack:
#         # set up
#         yield
#         # run the scene
#         yield next_scene, how_to_transition
#     # tear down


async def run(first_scene: Scene | str, *, parent: Widget=None, userdata: UserData=None):
    yield_prohibited_await = _yield_prohibited_await
    nullctx = contextlib.nullcontext()
    if parent is None:
        from kivy.app import App
        parent = App.get_running_app().root
    inuse_agens: list[AsyncGenerator] = []

    cur_scene = None
    transition = None
    next_scene = first_scene
    try:
        while True:
            if isinstance(next_scene, str):
                next_scene = _import_scene(next_scene)
            next_agen = next_scene(parent, userdata)
            if not isasyncgen(next_agen):
                raise TypeError(f"{next_scene} didn't return an async generator")
            inuse_agens.append(next_agen)
            async with transition or nullctx:
                if cur_scene is not None:
                    yield_prohibited_await(cur_agen.aclose())
                    inuse_agens.remove(cur_agen)
                r = yield_prohibited_await(next_agen.asend(None))
            if r is not None:
                raise RuntimeError(f"The first value yielded must be None, but got {r}.")
            cur_scene = next_scene
            cur_agen = next_agen
            next_scene, transition = await cur_agen.asend(None)
            if next_scene is None:
                return
    finally:
        for agen in inuse_agens:
            yield_prohibited_await(agen.aclose())
