__all__ = ("event", "event_freq", "suppress_event", "rest_of_touch_events", "rest_of_touch_events_cm", )

from collections.abc import AsyncIterator
import types
from functools import partial
from contextlib import asynccontextmanager, ExitStack

from asyncgui import _current_task, _sleep_forever, move_on_when, ExclusiveEvent, _wait_args


@types.coroutine
def event(event_dispatcher, event_name, *, filter=None, stop_dispatching=False):
    '''
    Returns an :class:`~collections.abc.Awaitable` that can be used to wait for:

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

      This only works for events not for properties.
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
    When handling a frequently occurring event, such as ``on_touch_move``, the following kind of code *might* cause
    performance issues:

    .. code-block::

        __, touch = await event(widget, 'on_touch_down')

        # This loop registers and unregisters an event handler on every iteration.
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

    .. versionadded:: 0.7.1

    .. versionchanged:: 0.9.0
        The ``free_to_await`` parameter was added.

    The ``free_to_await`` parameter:

    If set to False (the default), the only permitted async operation within the with-block is ``await xxx()``,
    where ``xxx`` is the identifier specified in the as-clause. To lift this restriction, set ``free_to_await`` to
    True — at the cost of slightly reduced performance.
    '''
    __slots__ = ('_disp', '_name', '_filter', '_stop', '_bind_id', '_free_to_await')

    def __init__(self, event_dispatcher, event_name, *, filter=None, stop_dispatching=False, free_to_await=False):
        self._disp = event_dispatcher
        self._name = event_name
        self._filter = filter
        self._stop = stop_dispatching
        self._free_to_await = free_to_await

    @types.coroutine
    def __aenter__(self):
        if self._free_to_await:
            e = ExclusiveEvent()
            self._bind_id = self._disp.fbind(self._name, partial(_event_callback, self._filter, e.fire, self._stop))
            return e.wait_args
        else:
            task = (yield _current_task)[0][0]
            self._bind_id = self._disp.fbind(
                self._name, partial(_event_callback, self._filter, task._step, self._stop))
            return _wait_args

    async def __aexit__(self, *args):
        self._disp.unbind_uid(self._name, self._bind_id)


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


async def rest_of_touch_events(widget, touch, *, stop_dispatching=False, grab=True) -> AsyncIterator[None]:
    '''
    Returns an async iterator that yields None on each ``on_touch_move`` event
    and stops when an ``on_touch_up`` event occurs.

    .. code-block::

        async for __ in rest_of_touch_events(widget, touch):
            print('on_touch_move')
        print('on_touch_up')

    :param grab: If set to ``False``, this API will not rely on ``touch.grab()``, which means there is no guarantee
                 that all events from the given touch will be delivered to the widget, `as documented <grab_>`_.
                 If the ``on_touch_up`` event is not delivered, the iterator will wait indefinitely for it—an event
                 that never comes. Do not set this to ``False`` unless you know what you are doing.
    :param stop_dispatching: Whether to stop dispatching non-grabbed touch events.
                             (Grabbed events are always stopped if the ``grab`` is ``True``.)
                             For details, see `event-bubbling`_.

    .. warning::
        You should not use this when Kivy is running in async mode. Use :func:`rest_of_touch_events_cm` instead.

    .. versionchanged:: 0.9.0
        The ``timeout`` parameter was removed.

    .. versionchanged:: 0.9.1
        The ``grab`` parameter was added.

    .. _grab: https://kivy.org/doc/master/guide/inputs.html#grabbing-touch-events
    .. _event-bubbling: https://kivy.org/doc/master/api-kivy.uix.widget.html#widget-touch-event-bubbling
    '''
    async with rest_of_touch_events_cm(widget, touch, stop_dispatching=stop_dispatching, grab=grab) as on_touch_move:
        while True:
            await on_touch_move()
            yield


@asynccontextmanager
async def rest_of_touch_events_cm(widget, touch, *, stop_dispatching=False, free_to_await=False, grab=True):
    '''
    A variant of :func:`rest_of_touch_events`.
    This version is more verbose, but remains safe even when Kivy is running in async mode.

    .. code-block::

        async with rest_of_touch_events_cm(widget, touch) as on_touch_move:
            while True:
                await on_touch_move()
                print('on_touch_move')
        print('on_touch_up')

    .. versionadded:: 0.9.1
    '''
    def is_the_same_touch(w, t, touch=touch):
        return t is touch
    with ExitStack() as stack:
        if grab:
            touch.grab(widget)
            stack.callback(touch.ungrab, widget)
            if stop_dispatching:
                ec = stack.enter_context
                se = partial(suppress_event, widget, filter=is_the_same_touch)
                ec(se('on_touch_up'))
                ec(se('on_touch_move'))

            def filter(w, t, touch=touch):
                return t is touch and t.grab_current is w
            stop_dispatching = True
        else:
            filter = is_the_same_touch
        async with (
            move_on_when(event(widget, 'on_touch_up', filter=filter, stop_dispatching=stop_dispatching)),
            event_freq(widget, 'on_touch_move', filter=filter, stop_dispatching=stop_dispatching,
                       free_to_await=free_to_await) as on_touch_move,
        ):
            yield on_touch_move
