__all__ = ('watch_touch', 'rest_of_touch_moves', )

import types
import functools
import asynckivy as ak


class watch_touch:
    '''
    Return an async context manager that provides an easy way to handle touch events.

    Usage
    -----

    .. code-block:: python

        async with watch_touch(widget, touch) as is_touch_move:
            while await is_touch_move():
                print('on_touch_move')
            else:
                print('on_touch_up')

    Restriction
    -----------

    1. The only thing you can 'await' inside the context manager is that the return value of the callable that is
       bound to the identifier in the as-clause.

       .. code-block:: python

           async with watch_touch(widget, touch) as is_touch_move:
               await is_touch_move()  # ALLOWED
               await something_else   # NOT ALLOWED

    2. Since the context manager grabs/ungrabs the ``touch``, the ``widget`` must NOT grab/ungrab it. Most of the
       widgets that interact to touches (``Button``, ``ScrollView`` and ``Carousel``, for instance) wouldn't work with
       this context manager unless you use it in a specific way.
    '''
    __slots__ = ('_widget', '_touch', '_stop_dispatching', '_timeout', '_uid_up', '_uid_move', '_no_cleanup', )

    def __init__(self, widget, touch, stop_dispatching=False, timeout=1.):
        self._widget = widget
        self._touch = touch
        self._stop_dispatching = stop_dispatching
        self._timeout = timeout
        self._no_cleanup = False

    def _on_touch_up_sd(step_coro, touch, w, t):
        if t is touch:
            if t.grab_current is w:
                t.ungrab(w)
                step_coro(False)
            return True

    def _on_touch_move_sd(step_coro, touch, w, t):
        if t is touch:
            if t.grab_current is w:
                step_coro(True)
            return True

    def _on_touch_up(step_coro, touch, w, t):
        if t.grab_current is w and t is touch:
            t.ungrab(w)
            step_coro(False)
            return True

    def _on_touch_move(step_coro, touch, w, t):
        if t.grab_current is w and t is touch:
            step_coro(True)
            return True

    _callbacks = ((_on_touch_up_sd, _on_touch_move_sd, ), (_on_touch_up, _on_touch_move, ), )
    del _on_touch_up, _on_touch_move, _on_touch_up_sd, _on_touch_move_sd

    @types.coroutine
    def _true_if_touch_move_false_if_touch_up() -> bool:
        return (yield lambda step_coro: None)[0][0]

    @types.coroutine
    def _always_false() -> bool:
        return False
        yield  # just to make this function a generator function

    async def __aenter__(
        self, get_step_coro=ak.get_step_coro, partial=functools.partial, _callbacks=_callbacks, ak=ak,
        _always_false=_always_false, _true_if_touch_move_false_if_touch_up=_true_if_touch_move_false_if_touch_up,
    ):
        touch = self._touch
        widget = self._widget
        if touch.time_end != -1:
            # `on_touch_up` might have been already fired so we need to find out it actually was or not.
            tasks = await ak.or_(
                ak.sleep(self._timeout),
                ak.event(widget, 'on_touch_up', filter=lambda w, t: t is touch),
            )
            if tasks[0].done:
                raise ak.MotionEventAlreadyEndedError(f"MotionEvent(uid={touch.uid}) has already ended")
            self._no_cleanup = True
            return _always_false
        step_coro = await get_step_coro()
        on_touch_up, on_touch_move = _callbacks[not self._stop_dispatching]
        touch.grab(widget)
        self._uid_up = widget.fbind('on_touch_up', partial(on_touch_up, step_coro, touch))
        self._uid_move = widget.fbind('on_touch_move', partial(on_touch_move, step_coro, touch))
        assert self._uid_up
        assert self._uid_move
        return _true_if_touch_move_false_if_touch_up

    del _always_false, _true_if_touch_move_false_if_touch_up, _callbacks

    async def __aexit__(self, *args):
        if self._no_cleanup:
            return
        w = self._widget
        self._touch.ungrab(w)
        w.unbind_uid('on_touch_up', self._uid_up)
        w.unbind_uid('on_touch_move', self._uid_move)


async def rest_of_touch_moves(widget, touch, *, stop_dispatching=False, timeout=1.):
    '''
    Wrap ``watch_touch()`` in a more intuitive interface.

    Usage
    -----

    .. code-block:: python

        async for __ in rest_of_touch_moves(widget, touch):
            print('on_touch_move')
        else:
            print('on_touch_up')

    Restriction
    -----------

    1. You are not allowed to 'await' anything during the iterations.

       .. code-block:: python

           async for __ in rest_of_touch_moves(widget, touch):
               await something  # <- NOT ALLOWED

    2. Like ``watch_touch``, this wouldn't work with the widgets that interact to touches.

    Downside compared to ``watch_touch``
    ------------------------------------

    1. Since this creates an async generator, it may not work if Kivy is running in asyncio/trio mode.
       See https://peps.python.org/pep-0525/#finalization for details.
    '''

    async with watch_touch(widget, touch, stop_dispatching, timeout) as is_touch_move:
        while await is_touch_move():
            yield
