__all__ = ('all_touch_moves', )

import types


async def _all_touch_moves_simple_ver(widget, touch):
    '''Returns an async-generator, which yields the touch when `on_touch_move`
    is fired, and ends when `on_touch_up` is fired. Grabs and ungrabs the
    touch automatically.
    '''
    from ._core import or_
    from ._event import event

    touch.grab(widget)
    try:
        while True:
            tasks = await or_(
                event(
                    widget, 'on_touch_move',
                    filter=lambda w, t: t.grab_current is w and t is touch,
                ),
                event(
                    widget, 'on_touch_up',
                    filter=lambda w, t: t.grab_current is w and t is touch,
                ),
            )
            if tasks[0].done:
                yield touch
            else:
                return
    finally:
        touch.ungrab(widget)


async def _all_touch_moves_complicated_ver(widget, touch):
    '''Does the same thing as `_all_touch_moves_simple_ver` does, but more
    faster.
    '''
    touch.grab(widget)
    ctx = {'touch': touch, }
    uid_up = widget.fbind('on_touch_up', _on_touch_up, ctx)
    uid_move = widget.fbind('on_touch_move', _on_touch_move, ctx)
    assert uid_up
    assert uid_move
    try:
        await _set_step_coro(ctx)
        while True:
            if await _touch_up_or_touch_move():
                return
            yield touch
    finally:
        widget.unbind_uid('on_touch_up', uid_up)
        widget.unbind_uid('on_touch_move', uid_move)


def _on_touch_up(ctx, w, t):
    if t.grab_current is w and t is ctx['touch']:
        t.ungrab(w)
        ctx['step_coro'](True)
        return True


def _on_touch_move(ctx, w, t):
    if t.grab_current is w and t is ctx['touch']:
        ctx['step_coro'](False)
        return True


@types.coroutine
def _set_step_coro(ctx):
    yield lambda step_coro: (ctx.__setitem__('step_coro', step_coro), step_coro())


@types.coroutine
def _touch_up_or_touch_move() -> bool:
    '''Returns True if `on_touch_up` is fired, False if `on_touch_move`
    is fired.'''
    return (yield lambda step_coro: None)[0][0]


all_touch_moves = _all_touch_moves_complicated_ver
