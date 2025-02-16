__all__ = ('rest_of_touch_events', )

import typing as T
from functools import partial
from contextlib import nullcontext
from asyncgui import wait_any, move_on_when
from ._exceptions import MotionEventAlreadyEndedError
from ._sleep import sleep
from ._event import event, event_freq
from ._utils import suppress_event


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
