__all__ = ("event", "event_freq", "suppress_event", "rest_of_touch_events", )

import typing as T
import types
from functools import partial
from contextlib import ExitStack

from asyncgui import _current_task, _sleep_forever, move_on_when


@types.coroutine
def event(event_dispatcher, event_name, *, filter=None, stop_dispatching=False) -> T.Awaitable[tuple]:
    '''
    Returns an awaitable that can be used to wait for:

    * a Kivy event to occur.
    * a Kivy property's value to change.

    .. code-block::

        # Wait for a button to be pressed.
        await event(button, 'on_press')

        # Wait for an 'on_touch_down' event to occur.
        __, touch = await event(widget, 'on_touch_down')

        # Wait for 'widget.x' to change.
        __, x = await ak.event(widget, 'x')

    The ``filter`` parameter:

    .. code-block::

        # Wait for an 'on_touch_down' event to occur inside a widget.
        __, touch = await event(widget, 'on_touch_down', filter=lambda w, t: w.collide_point(*t.opos))

        # Wait for 'widget.x' to become greater than 100.
        if widget.x <= 100:
            await event(widget, 'x', filter=lambda __, x: x > 100)

    The ``stop_dispatching`` parameter:

      It only works for events not for properties.
      See :ref:`kivys-event-system` for details.
    '''
    task = (yield _current_task)[0][0]
    bind_id = event_dispatcher.fbind(event_name, partial(_event_callback, filter, task._step, stop_dispatching))
    assert bind_id  # check if binding succeeded
    try:
        return (yield _sleep_forever)[0]
    finally:
        event_dispatcher.unbind_uid(event_name, bind_id)


def _event_callback(filter, task_step, stop_dispatching, *args, **kwargs):
    if (filter is None) or filter(*args, **kwargs):
        task_step(*args)
        return stop_dispatching


class event_freq:
    '''
    When handling a frequently occurring event, such as ``on_touch_move``, the following code might cause performance
    issues:

    .. code-block::

        __, touch = await event(widget, 'on_touch_down')
        while True:
            await event(widget, 'on_touch_move', filter=lambda w, t: t is touch)
            ...

    If that happens, try the following code instead. It might resolve the issue:

    .. code-block::

        __, touch = await event(widget, 'on_touch_down')
        async with event_freq(widget, 'on_touch_move', filter=lambda w, t: t is touch) as on_touch_move:
            while True:
                await on_touch_move()
                ...

    The trade-off is that within the context manager, you can't perform any async operations except the
    ``await on_touch_move()``.

    .. code-block::

        async with event_freq(...) as xxx:
            await xxx()  # OK
            await something_else()  # Don't

    .. versionadded:: 0.7.1
    '''
    __slots__ = ('_disp', '_name', '_filter', '_stop', '_bind_id', )

    def __init__(self, event_dispatcher, event_name, *, filter=None, stop_dispatching=False):
        self._disp = event_dispatcher
        self._name = event_name
        self._filter = filter
        self._stop = stop_dispatching

    @types.coroutine
    def __aenter__(self):
        task = (yield _current_task)[0][0]
        self._bind_id = self._disp.fbind(self._name, partial(_event_callback, self._filter, task._step, self._stop))
        return self._wait_one

    async def __aexit__(self, *args):
        self._disp.unbind_uid(self._name, self._bind_id)

    @staticmethod
    @types.coroutine
    def _wait_one():
        return (yield _sleep_forever)[0]


class suppress_event:
    '''
    Returns a context manager that prevents the callback functions (including the default handler) bound to an event
    from being called.

    .. code-block::
        :emphasize-lines: 4

        from kivy.uix.button import Button

        btn = Button()
        btn.bind(on_press=lambda __: print("pressed"))
        with suppress_event(btn, 'on_press'):
            btn.dispatch('on_press')

    The above code prints nothing because the callback function won't be called.

    Strictly speaking, this context manager doesn't prevent all callback functions from being called.
    It only prevents the callback functions that were bound to an event before the context manager enters.
    Thus, the following code prints ``pressed``.

    .. code-block::
        :emphasize-lines: 5

        from kivy.uix.button import Button

        btn = Button()
        with suppress_event(btn, 'on_press'):
            btn.bind(on_press=lambda __: print("pressed"))
            btn.dispatch('on_press')

    .. warning::

        You need to be careful when you suppress an ``on_touch_xxx`` event.
        See :ref:`kivys-event-system` for details.
    '''
    __slots__ = ('_dispatcher', '_name', '_bind_uid', '_filter', )

    def __init__(self, event_dispatcher, event_name, *, filter=lambda *args, **kwargs: True):
        self._dispatcher = event_dispatcher
        self._name = event_name
        self._filter = filter

    def __enter__(self):
        self._bind_uid = self._dispatcher.fbind(self._name, self._filter)

    def __exit__(self, *args):
        self._dispatcher.unbind_uid(self._name, self._bind_uid)


async def rest_of_touch_events(widget, touch, *, stop_dispatching=False) -> T.AsyncIterator[None]:
    '''
    Returns an async iterator that yields None on each ``on_touch_move`` event
    and stops when an ``on_touch_up`` event occurs.

    .. code-block::

        async for __ in rest_of_touch_events(widget, touch):
            print('on_touch_move')
        print('on_touch_up')

    :param stop_dispatching: If the ``widget`` is a type that grabs touches on its own, such as
                             :class:`kivy.uix.button.Button`, you'll likely want to set this to True
                             in most cases to avoid grab conflicts.

    .. versionchanged:: 0.9.0
        The ``timeout`` parameter was removed.
        You are now responsible for handling cases where the ``on_touch_up`` event for the touch does not occur.
        If you fail to handle this, the iterator will wait indefinitely for an event that never comes.
    '''
    touch.grab(widget)
    try:
        with ExitStack() as stack:
            if stop_dispatching:
                se = partial(suppress_event, widget, filter=lambda w, t, touch=touch: t is touch)
                stack.enter_context(se("on_touch_up"))
                stack.enter_context(se("on_touch_move"))

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
