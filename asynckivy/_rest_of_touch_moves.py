__all__ = ('rest_of_touch_moves', )

import types
from functools import partial
from asynckivy import or_, sleep, event, get_step_coro, MotionEventAlreadyEndedError


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


async def rest_of_touch_moves(widget, touch, *, stop_dispatching=False, timeout=1.):
    '''
    Returns an async-generator that iterates the number of times
    `on_touch_move` is fired, and ends when `on_touch_up` is fired. Grabs and
    ungrabs the touch automatically. If `stop_dispatching` is True, the touch
    will never be dispatched further i.e. the next widget will never get this
    touch until the generator ends. If `on_touch_up` was already fired,
    `MotionEventAlreadyEndedError` will be raised.
    '''
    if touch.time_end != -1:
        # `on_touch_up` might have been already fired so we need to find out
        # it actually was or not.
        tasks = await or_(
            sleep(timeout),
            event(widget, 'on_touch_up', filter=lambda w, t: t is touch),
        )
        if tasks[0].done:
            raise MotionEventAlreadyEndedError(
                f"MotionEvent(uid={touch.uid}) has already ended")
        else:
            return

    step_coro = await get_step_coro()
    on_touch_up, on_touch_move = _callbacks[not stop_dispatching]
    on_touch_up = partial(on_touch_up, step_coro, touch)
    on_touch_move = partial(on_touch_move, step_coro, touch)

    touch.grab(widget)
    uid_up = widget.fbind('on_touch_up', on_touch_up)
    uid_move = widget.fbind('on_touch_move', on_touch_move)
    assert uid_up
    assert uid_move

    # LOAD_FAST
    true_if_touch_move_false_if_touch_up = _true_if_touch_move_false_if_touch_up

    try:
        while await true_if_touch_move_false_if_touch_up():
            yield
    finally:
        touch.ungrab(widget)
        widget.unbind_uid('on_touch_up', uid_up)
        widget.unbind_uid('on_touch_move', uid_move)


@types.coroutine
def _true_if_touch_move_false_if_touch_up() -> bool:
    return (yield lambda step_coro: None)[0][0]
