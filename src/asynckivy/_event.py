__all__ = ('event', )

import typing as T
from functools import partial
from asyncgui import AsyncEvent


async def event(event_dispatcher, event_name, *, filter=None, stop_dispatching=False) -> T.Awaitable[tuple]:
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
    ev = AsyncEvent()
    bind_id = event_dispatcher.fbind(event_name, partial(_callback, filter, ev, stop_dispatching))
    assert bind_id  # check if binding succeeded
    try:
        return (await ev.wait())[0]
    finally:
        event_dispatcher.unbind_uid(event_name, bind_id)


def _callback(filter, ev, stop_dispatching, *args, **kwargs):
    if (filter is None) or filter(*args, **kwargs):
        ev.fire(*args)
        return stop_dispatching
