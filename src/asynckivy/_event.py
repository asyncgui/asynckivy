__all__ = ('event', )

import typing as T
from functools import partial
from asyncgui import IBox
from kivy.event import EventDispatcher


async def event(ed: EventDispatcher, name: str, /, *, filter=None, stop_dispatching=False) -> T.Awaitable[tuple]:
    '''
    Return an awaitable that can be used to wait for:

    * a Kivy event to occur.
    * the value of a Kivy property to transition.

    .. code-block::

        # Wait for a button to be pressed.
        await event(button, 'on_press')

        # Wait for an 'on_touch_down' event to occur.
        __, touch = await event(widget, 'on_touch_down')

        # Wait 'widget.x' to transition.
        __, x = await ak.event(widget, 'x')


    The ``filter`` parameter can be used to apply a filter to the object you are waiting for.

    .. code-block::

        # Wait for an 'on_touch_down' event to occur inside a widget.
        __, touch = await event(widget, 'on_touch_down', filter=lambda w, t: w.collide_point(*t.opos))

        # Wait for 'widget.x' to become greater than 100.
        if widget.x <= 100:
            await event(widget, 'x', filter=lambda __, x: x > 100)

    As for ``stop_dispatching``, see :ref:`kivys-event-system`.
    '''
    box = IBox()
    bind_id = ed.fbind(name, partial(_callback, filter, box, stop_dispatching))
    assert bind_id  # check if binding succeeded
    try:
        return (await box.get())[0]
    finally:
        ed.unbind_uid(name, bind_id)


def _callback(filter, box, stop_dispatching, *args, **kwargs):
    if (filter is None) or filter(*args, **kwargs):
        box.put(*args)
        return stop_dispatching
