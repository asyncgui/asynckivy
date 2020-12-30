__all__ = ('event', )

import types


@types.coroutine
def event(ed, name, *, filter=None, return_value=None):
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
           # wait for a widget to fire a 'on_touch_down'
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
               await ak.event(
                   widget, 'x',
                   filter=lambda widget, x: x > 100)

    ``return_value`` is useful when the return-value of callbacks is important
    like ``on_touch_xxx``.

    .. code-block:: python

       import asynckivy as ak

       async def async_fn(label):
           # wait for a label to get touched inside of it, and stop the
           # event-dispatching when it happened.
           await ak.event(
               label, 'on_touch_down', return_value=True,
               filter=lambda label, touch: label.collide_point(*touch.opos),
           )
    '''
    bind_id = None
    step_coro = None

    def bind(step_coro_):
        nonlocal bind_id, step_coro
        bind_id = ed.fbind(name, callback)
        assert bind_id  # check if binding succeeded
        step_coro = step_coro_

    def callback(*args, **kwargs):
        if (filter is not None) and (not filter(*args, **kwargs)):
            return
        ed.unbind_uid(name, bind_id)
        step_coro(*args, **kwargs)
        return return_value

    return (yield bind)[0]
