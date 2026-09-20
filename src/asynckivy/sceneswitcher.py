__all__ = ("run", "SceneSwitcherError", )

from collections.abc import Callable, AsyncGenerator
from typing import TypeAlias, Any
from inspect import isasyncgen
from importlib import import_module
import contextlib

from kivy.uix.widget import Widget

import asynckivy as ak

UserData: TypeAlias = Any
Scene: TypeAlias = Callable[[Widget, UserData], AsyncGenerator]


def _import_scene(absolute_name: str) -> Scene:
    module_name, scene_name = absolute_name.rsplit(".", 1)
    return getattr(import_module(module_name), scene_name)


class SceneSwitcherError(Exception):
    '''
    Base class for all exceptions raised by the ``sceneswitcher`` submodule.

    .. versionadded:: 0.11.1
    '''


async def _empty_scene(parent: Widget, userdata: Any):
    yield
    yield None, None


async def run(first_scene: Scene | str, first_transition=None, *, parent: Widget, userdata: Any=None):
    '''
    .. versionadded:: 0.11.1
    '''
    empty_scene = _empty_scene
    nullctx = contextlib.nullcontext()
    inuse_agens: list[AsyncGenerator] = []

    cur_scene = None
    cur_agen = None
    transition = first_transition
    next_scene = first_scene
    try:
        while True:
            if next_scene is None:
                next_scene = empty_scene
            elif isinstance(next_scene, str):
                next_scene = _import_scene(next_scene)
            next_agen = next_scene(parent, userdata)
            if not isasyncgen(next_agen):
                raise SceneSwitcherError(f"{next_scene} didn't return an async generator")
            inuse_agens.append(next_agen)
            with ak.block_touch_events(parent):
                async with nullctx if transition is None else transition(parent):
                    if cur_scene is not None:
                        await cur_agen.aclose()
                        inuse_agens.remove(cur_agen)
                    r = await next_agen.asend(None)
                    if r is not None:
                        raise SceneSwitcherError(f"The first value yielded must be None, but got {repr(r)}.")
            if next_scene is empty_scene:
                return
            cur_scene = next_scene
            cur_agen = next_agen
            next_scene, transition = await cur_agen.asend(None)
    finally:
        for agen in inuse_agens:
            await agen.aclose()
