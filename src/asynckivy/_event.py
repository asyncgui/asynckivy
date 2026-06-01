from functools import partial
from contextlib import asynccontextmanager, ExitStack

from asyncgui import move_on_when, ExclusiveEvent


async def event(event_dispatcher, event_name, *, filter=None, stop_dispatching=False):
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
    e = ExclusiveEvent()
    bind_id = event_dispatcher.fbind(event_name, partial(_event_callback, filter, e.fire, stop_dispatching))
    assert bind_id  # check if binding succeeded
    try:
        return await e.wait_args()
    finally:
        event_dispatcher.unbind_uid(event_name, bind_id)


def _event_callback(filter, callback, stop_dispatching, *args, **kwargs):
    if (filter is None) or filter(*args, **kwargs):
        callback(*args)
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

        with event_freq(widget, "on_touch_move", filter=lambda w, t: t is touch) as on_touch_move:
            while True:
                await on_touch_move()
                ...

    When listening for an ``on_touch_move`` event, you will often also want to listen for an ``on_touch_up`` event,
    which leads to deeply nested code:

    .. code-block::

        __, touch = await event(widget, "on_touch_down")

        def is_the_same_touch(w, t, touch=touch):
            return t is touch
        async with move_on_when(event(widget, "on_touch_up", filter=is_the_same_touch)):
            with event_freq(widget, "on_touch_move", filter=is_the_same_touch) as on_touch_move:
                while True:
                    await on_touch_move()
                    ...

    To mitigate this, ``event_freq`` can also be used as an async context manager, making the above code less nested:

    .. code-block::

        async with (
            move_on_when(event(widget, "on_touch_up", filter=is_the_same_touch)),
            event_freq(widget, "on_touch_move", filter=is_the_same_touch) as on_touch_move,
        ):
            while True:
                await on_touch_move()
                ...

    .. versionadded:: 0.7.1

    .. versionchanged:: 0.9.0
        The ``free_to_await`` parameter was added.

    .. versionchanged:: 0.11.0

        * This can be used as either a synchronous or an asynchronous context manager.
          Prefer the synchronous form, as it has less overhead.
        * The ``free_to_await`` parameter was removed. You can treat it as if it were always set to True.
    '''
    __slots__ = ("_disp", "_name", "_filter", "_stop", "_bind_id", )

    def __init__(self, event_dispatcher, event_name, *, filter=None, stop_dispatching=False):
        self._disp = event_dispatcher
        self._name = event_name
        self._filter = filter
        self._stop = stop_dispatching

    def __enter__(self):
        e = ExclusiveEvent()
        self._bind_id = self._disp.fbind(self._name, partial(_event_callback, self._filter, e.fire, self._stop))
        return e.wait_args

    def __exit__(self, *args):
        self._disp.unbind_uid(self._name, self._bind_id)

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, *args):
        return self.__exit__(*args)


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


class block_touch_events:
    '''
    .. code-block::

        with block_touch_events(widget):
            ...

    Returns a context manager that blocks all touch events that meet **both** of the following criteria:

    * The touch is not currently grabbed by any widget. (i.e. ``touch.grab_current is None``)
    * The touch is inside the widget's bounding box. (i.e. ``widget.collide_point(*touch.pos)``)

    Basically equivalent to the following:

    .. code-block::

        def f(w, t):
            return t.grab_current is None and w.collide_point(*t.pos)
        with (
            suppress_event(widget, 'on_touch_down', filter=f),
            suppress_event(widget, 'on_touch_move', filter=f),
            suppress_event(widget, 'on_touch_up', filter=f),
        ):
            ...

    .. versionadded:: 0.10.0
    '''
    __slots__ = ('_dispatcher', '_filter', )

    def __init__(self, event_dispatcher, *, filter=lambda w, t: t.grab_current is None and w.collide_point(*t.pos)):
        self._dispatcher = event_dispatcher
        self._filter = filter

    def __enter__(self):
        f = self._filter
        self._dispatcher.bind(on_touch_down=f, on_touch_move=f, on_touch_up=f)

    def __exit__(self, *__):
        f = self._filter
        self._dispatcher.unbind(on_touch_down=f, on_touch_move=f, on_touch_up=f)


@asynccontextmanager
async def rest_of_touch_events(widget, touch, *, stop_dispatching=False, grab=True):
    '''
    Returns an async context manager that helps to await both ``on_touch_move`` and
    ``on_touch_up`` events at the same time.

    .. code-block::

        async with rest_of_touch_events(widget, touch) as on_touch_move:
            while True:
                await on_touch_move()
                print("touch moved")
        print("touch ended")

    :param grab:
        If set to ``False``, this API will not rely on ``touch.grab()``, which means there is no guarantee
        that all events from the given touch will be delivered to the widget, as documented in
        `grabbing-touch-events`_. If the corresponding ``on_touch_up`` event is not delivered, the
        ``await on_touch_move()`` line will wait indefinitely for it.
        Do not set this to ``False`` unless you know what you are doing.

    :param stop_dispatching:
        Whether to stop dispatching non-grabbed touch events corresponding to the given touch.
        (Grabbed touch events are always stopped if the ``grab`` is ``True``, and are never stopped
        if the ``grab`` is ``False``.) For details, see `event-bubbling`_.

    .. versionadded:: 0.9.1

    .. versionchanged:: 0.11.0

        * The ``free_to_await`` parameter was removed. You can treat it as if it were always set to True.
        * The API renamed from ``rest_of_touch_events_cm`` to ``rest_of_touch_events``.
          The original ``rest_of_touch_events`` was removed.

    .. _grabbing-touch-events: https://kivy.org/doc/master/guide/inputs.html#grabbing-touch-events
    .. _event-bubbling: https://kivy.org/doc/master/api-kivy.uix.widget.html#widget-touch-event-bubbling
    '''
    with ExitStack() as stack:
        ec = stack.enter_context

        if stop_dispatching:
            if grab:
                def filter(w, t, touch=touch):
                    return t is touch
            else:
                def filter(w, t, touch=touch):
                    return t is touch and t.grab_current is not w
        elif grab:
            def filter(w, t, touch=touch):
                return t is touch and t.grab_current is w
        else:
            filter = None
        if filter is not None:
            se = partial(suppress_event, widget, filter=filter)
            ec(se("on_touch_up"))
            ec(se("on_touch_move"))

        if grab:
            touch.grab(widget)
            stack.callback(touch.ungrab, widget)

            def filter(w, t, touch=touch):
                return t is touch and t.grab_current is w
            stop_dispatching = True
        else:
            def filter(w, t, touch=touch):
                return t is touch and t.grab_current is None

        on_touch_move = ec(event_freq(widget, "on_touch_move", filter=filter, stop_dispatching=stop_dispatching))
        async with move_on_when(event(widget, "on_touch_up", filter=filter, stop_dispatching=stop_dispatching)):
            yield on_touch_move


@asynccontextmanager
async def visibility_aware_touch_events(widget, touch, *, stop_dispatching=False):
    '''
    (experimental)
    :func:`rest_of_touch_events` with awareness of whether the touch is currently within
    the widget's visible area. This can be useful when a widget is clipped by other
    widgets and you need to know whether the touch is inside the portion that is
    actually visible.

    .. code-block::

        __, touch = await event(widget, "on_touch_down")
        was_inside = widget.collide_point(*touch.pos)

        async with visibility_aware_touch_events(widget, touch) as on_touch_move:
            while True:
                is_inside = await on_touch_move()
                if is_inside:
                    if was_inside:
                        print("Touch moved while staying within the visible area")
                    else:
                        print("Touch moved from outside to inside the visible area")
                else:
                    if was_inside:
                        print("Touch moved from inside to outside the visible area")
                    else:
                        print("Touch moved while staying outside the visible area")
                was_inside = is_inside
        print("Touch ended.")

    .. warning::
        Since :class:`~kivy.uix.scrollview.ScrollView` does not dispatch touch events
        to its children for touches that start outside it, this API will not work
        properly if a ScrollView is in the target widget's parent hierarchy and the
        touch starts outside the ScrollView.

    .. versionadded:: 0.11.0
    '''
    e = ExclusiveEvent()
    inside = False

    def on_touch_move(w, t, touch=touch, collide_point=widget.collide_point, fire=e.fire,
                      stop_dispatching=stop_dispatching):
        nonlocal inside
        if t is not touch:
            return
        if t.grab_current is w:
            fire(inside)
            inside = False
            return True
        inside = collide_point(*t.pos)
        return stop_dispatching

    with ExitStack() as stack:
        touch.grab(widget)
        stack.callback(touch.ungrab, widget)
        stack.callback(widget.unbind_uid, "on_touch_move", widget.fbind("on_touch_move", on_touch_move))
        if stop_dispatching:
            stack.enter_context(suppress_event(widget, "on_touch_up", filter=lambda w, t: t is touch))
        async with move_on_when(
            event(widget, "on_touch_up", filter=lambda w, t: t is touch and t.grab_current is w, stop_dispatching=True)
        ):
            yield e.wait_args_0
