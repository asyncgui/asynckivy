__all__ = ('event', )

from functools import partial
from asyncgui import IBox


async def event(ed, name, *, filter=None, stop_dispatching=False):
    '''
    event
    =====

    Returns an awaitable that can be used to wait for:

    * Kivy events to get fired
    * Kivy properties to change

    Usage
    -----

    .. code-block:: python

       import asynckivy as ak

       async def async_fn(widget):
           # wait for a widget to fire an 'on_touch_down' event.
           __, touch = await ak.event(widget, 'on_touch_down')
           if widget.collide_point(*touch.opos):
               print('Someone touched me.')

           # wait for 'widget.x' to change
           __, x = await ak.event(widget, 'x')
           print(f"x was set to {x}")

    ``filter`` is useful when you want to give it a condition.

    .. code-block:: python

       import asynckivy as ak

       async def async_fn(widget):
           # wait for a widget to get touched inside of it
           await ak.event(
               widget, 'on_touch_down',
               filter=lambda widget, touch: widget.collide_point(*touch.opos)
           )

           # wait for 'widget.x' to become greater than 100
           if widget.x <= 100:
               await ak.event(widget, 'x', filter=lambda __, x: x > 100)

    ``stop_dispatching`` is useful when you want to stop event-dispatching
    there.

    .. code-block:: python

       import asynckivy as ak

       async def async_fn(label):
           # wait for a label to get touched inside of it, and stop the
           # event-dispatching when that happened.
           await ak.event(
               label, 'on_touch_down', stop_dispatching=True,
               filter=lambda label, touch: label.collide_point(*touch.opos),
           )
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
