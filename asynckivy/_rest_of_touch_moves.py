__all__ = ('rest_of_touch_moves', )

import types


async def rest_of_touch_moves(widget, touch, *, stop_dispatching=False):
    '''Returns an async-generator that yields the given touch when
    `on_touch_move` is fired, and ends when `on_touch_up` is fired. Grabs and
    ungrabs the touch automatically. If `stop_dispatching` is True, the touch
    will never be dispatched further i.e. the next widget will never get this
    touch until the generator ends. If `on_touch_up` was already fired,
    `MotionEventAlreadyEndedError` will be raised.
    '''
    from asyncgui import get_step_coro
    from asynckivy import or_, sleep, event
    from asynckivy.exceptions import MotionEventAlreadyEndedError

    step_coro = await get_step_coro()
    if touch.time_end != -1:
        # `on_touch_up` might be already fired. If so raise an exception.
        tasks = await or_(
            sleep(0),
            event(widget, 'on_touch_up', filter=lambda w, t: t is touch),
        )
        if tasks[0].done:
            raise MotionEventAlreadyEndedError(
                f"MotionEvent(uid={touch.uid}) has already ended")
        else:
            return

    if stop_dispatching:
        def _on_touch_up(w, t):
            if t is touch:
                if t.grab_current is w:
                    t.ungrab(w)
                    step_coro(False)
                return True

        def _on_touch_move(w, t):
            if t is touch:
                if t.grab_current is w:
                    step_coro(True)
                return True
    else:
        def _on_touch_up(w, t):
            if t.grab_current is w and t is touch:
                t.ungrab(w)
                step_coro(False)
                return True

        def _on_touch_move(w, t):
            if t.grab_current is w and t is touch:
                step_coro(True)
                return True

    touch.grab(widget)
    uid_up = widget.fbind('on_touch_up', _on_touch_up)
    uid_move = widget.fbind('on_touch_move', _on_touch_move)
    assert uid_up
    assert uid_move

    # assigning to a local variable might improve performance
    true_if_touch_move_false_if_touch_up = \
        _true_if_touch_move_false_if_touch_up

    try:
        while await true_if_touch_move_false_if_touch_up():
            yield touch
    finally:
        touch.ungrab(widget)
        widget.unbind_uid('on_touch_up', uid_up)
        widget.unbind_uid('on_touch_move', uid_move)


@types.coroutine
def _true_if_touch_move_false_if_touch_up() -> bool:
    return (yield lambda step_coro: None)[0][0]
