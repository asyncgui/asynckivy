__all__ = ('watch_touch', 'rest_of_touch_events', )

import typing as T
import types
from functools import partial
from contextlib import nullcontext
from asyncgui import wait_any, current_task, move_on_when
from ._exceptions import MotionEventAlreadyEndedError
from ._sleep import sleep
from ._event import event, event_freq
from ._utils import suppress_event


class watch_touch:
    '''
    Returns an async context manager that provides an easy way to handle touch events.

    .. code-block::

        async with watch_touch(widget, touch) as in_progress:
            while await in_progress():
                print('on_touch_move')
            print('on_touch_up')

    The ``await in_progress()`` waits for either an ``on_touch_move`` event or an ``on_touch_up`` event to occur, and
    returns True or False respectively when they occurred.

    **Caution**

    * You are not allowed to perform any kind of async operations inside the with-block except ``await in_progress()``.

      .. code-block::

          async with watch_touch(widget, touch) as in_progress:
              await in_progress()  # OK
              await something_else  # NOT ALLOWED
              async with async_context_manager:  # NOT ALLOWED
                  ...
              async for __ in async_iterator:  # NOT ALLOWED
                  ...

    * If the ``widget`` is the type of widget that grabs touches by itself, such as :class:`kivy.uix.button.Button`,
      you probably want to set the ``stop_dispatching`` parameter to True in most cases.
    * There are widgets/behaviors that can simulate a touch (e.g. :class:`kivy.uix.scrollview.ScrollView`,
      :class:`kivy.uix.behaviors.DragBehavior` and ``kivy_garden.draggable.KXDraggableBehavior``).
      If many such widgets are in the parent stack of the ``widget``, this API might mistakenly raise a
      :exc:`asynckivy.MotionEventAlreadyEndedError`. If that happens, increase the ``timeout`` parameter.
    '''
    __slots__ = ('_widget', '_touch', '_stop_dispatching', '_timeout', '_uid_up', '_uid_move', '_no_cleanup', )

    def __init__(self, widget, touch, *, stop_dispatching=False, timeout=1.):
        self._widget = widget
        self._touch = touch
        self._stop_dispatching = stop_dispatching
        self._timeout = timeout
        self._no_cleanup = False

    def _on_touch_up_sd(step, touch, w, t):
        if t is touch:
            if t.grab_current is w:
                t.ungrab(w)
                step(False)
            return True

    def _on_touch_move_sd(step, touch, w, t):
        if t is touch:
            if t.grab_current is w:
                step(True)
            return True

    def _on_touch_up(step, touch, w, t):
        if t.grab_current is w and t is touch:
            t.ungrab(w)
            step(False)
            return True

    def _on_touch_move(step, touch, w, t):
        if t.grab_current is w and t is touch:
            step(True)
            return True

    _callbacks = ((_on_touch_up_sd, _on_touch_move_sd, ), (_on_touch_up, _on_touch_move, ), )
    del _on_touch_up, _on_touch_move, _on_touch_up_sd, _on_touch_move_sd

    @staticmethod
    @types.coroutine
    def _true_if_touch_move_false_if_touch_up() -> bool:
        return (yield lambda step_coro: None)[0][0]

    @staticmethod
    @types.coroutine
    def _always_false() -> bool:
        return False
        yield  # just to make this function a generator function

    async def __aenter__(self) -> T.Awaitable[T.Callable[[], T.Awaitable[bool]]]:
        touch = self._touch
        widget = self._widget
        if touch.time_end != -1:
            # `on_touch_up` might have been already fired so we need to find out it actually was or not.
            tasks = await wait_any(
                sleep(self._timeout),
                event(widget, 'on_touch_up', filter=lambda w, t: t is touch),
            )
            if tasks[0].finished:
                raise MotionEventAlreadyEndedError(f"MotionEvent(uid={touch.uid}) has already ended")
            self._no_cleanup = True
            return self._always_false
        step = (await current_task())._step
        on_touch_up, on_touch_move = self._callbacks[not self._stop_dispatching]
        touch.grab(widget)
        self._uid_up = widget.fbind('on_touch_up', partial(on_touch_up, step, touch))
        self._uid_move = widget.fbind('on_touch_move', partial(on_touch_move, step, touch))
        assert self._uid_up
        assert self._uid_move
        return self._true_if_touch_move_false_if_touch_up

    async def __aexit__(self, *args):
        if self._no_cleanup:
            return
        w = self._widget
        self._touch.ungrab(w)
        w.unbind_uid('on_touch_up', self._uid_up)
        w.unbind_uid('on_touch_move', self._uid_move)


async def rest_of_touch_events(widget, touch, *, stop_dispatching=False, timeout=1.) -> T.AsyncIterator[None]:
    '''
    Returns an async iterator that yields None on each ``on_touch_move`` event
    and stops when an ``on_touch_up`` event occurs.

    .. code-block::

        async for __ in rest_of_touch_events(widget, touch):
            print('on_touch_move')
        print('on_touch_up')

    **Caution**

    * If the ``widget`` is the type of widget that grabs touches by itself, such as :class:`kivy.uix.button.Button`,
      you probably want to set the ``stop_dispatching`` parameter to True in most cases.
    * There are widgets/behaviors that might simulate touch events (e.g. :class:`kivy.uix.scrollview.ScrollView`,
      :class:`kivy.uix.behaviors.DragBehavior` and ``kivy_garden.draggable.KXDraggableBehavior``).
      If many such widgets are in the parent stack of the ``widget``, this API might mistakenly raise a
      :exc:`asynckivy.MotionEventAlreadyEndedError`. If that happens, increase the ``timeout`` parameter.
    '''
    if touch.time_end != -1:
        # An `on_touch_up`` event might have already been fired, so we need to determine
        # whether it actually was or not.
        tasks = await wait_any(
            sleep(timeout),
            event(widget, 'on_touch_up', filter=lambda w, t: t is touch),
        )
        if tasks[0].finished:
            raise MotionEventAlreadyEndedError(f"MotionEvent(uid={touch.uid}) has already ended")
        return
    try:
        touch.grab(widget)
        if stop_dispatching:
            se = partial(suppress_event, widget, filter=lambda w, t, touch=touch: t is touch)
        with (
            se("on_touch_up") if stop_dispatching else nullcontext(),
            se("on_touch_move") if stop_dispatching else nullcontext(),
        ):
            def filter(w, t, touch=touch):
                return t is touch and t.grab_current is w
            async with (
                move_on_when(event(widget, "on_touch_up", filter=filter, stop_dispatching=True)),
                event_freq(widget, 'on_touch_move', filter=filter, stop_dispatching=True) as on_touch_move,
            ):
                while True:
                    await on_touch_move()
                    yield
    finally:
        touch.ungrab(widget)
