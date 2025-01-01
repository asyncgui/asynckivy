__all__ = ('event', 'event_freq', )

import typing as T
import types
from functools import partial
from asyncgui import _current_task, _sleep_forever


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
    bind_id = event_dispatcher.fbind(event_name, partial(_callback, filter, task._step, stop_dispatching))
    assert bind_id  # check if binding succeeded
    try:
        return (yield _sleep_forever)[0]
    finally:
        event_dispatcher.unbind_uid(event_name, bind_id)


def _callback(filter, task_step, stop_dispatching, *args, **kwargs):
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
        self._bind_id = self._disp.fbind(self._name, partial(_callback, self._filter, task._step, self._stop))
        return self._wait_one

    async def __aexit__(self, *args):
        self._disp.unbind_uid(self._name, self._bind_id)

    @staticmethod
    @types.coroutine
    def _wait_one():
        return (yield _sleep_forever)[0]
