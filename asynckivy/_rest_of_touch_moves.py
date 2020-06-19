__all__ = ('rest_of_touch_moves', )

import types


async def rest_of_touch_moves(widget, touch):
    '''Returns an async-generator, which yields the touch when `on_touch_move`
    is fired, and ends when `on_touch_up` is fired. Grabs and ungrabs the
    touch automatically.
    '''
    from asynckivy._core import _get_step_coro
    step_coro = await _get_step_coro()

    def _on_touch_up(w, t):
        if t.grab_current is w and t is touch:
            t.ungrab(w)
            step_coro(True)
            return True
    def _on_touch_move(w, t):
        if t.grab_current is w and t is touch:
            step_coro(False)
            return True

    touch.grab(widget)
    uid_up = widget.fbind('on_touch_up', _on_touch_up)
    uid_move = widget.fbind('on_touch_move', _on_touch_move)
    assert uid_up
    assert uid_move

    # assigning to a local variable might improve performance
    true_if_touch_up_false_if_touch_move = \
        _true_if_touch_up_false_if_touch_move

    try:
        while True:
            if await true_if_touch_up_false_if_touch_move():
                return
            yield touch
    finally:
        widget.unbind_uid('on_touch_up', uid_up)
        widget.unbind_uid('on_touch_move', uid_move)


@types.coroutine
def _true_if_touch_up_false_if_touch_move() -> bool:
    return (yield lambda step_coro: None)[0][0]


all_touch_moves = rest_of_touch_moves  # will be removed in the future
