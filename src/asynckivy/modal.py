__all__ = (
    'open', 'Transition', 'no_transition', 'FadeTransition', 'SlideTransition',
)

from typing import TypeAlias, Literal
from functools import partial
from collections.abc import Callable, AsyncIterator
from contextlib import AsyncExitStack, contextmanager, asynccontextmanager, AbstractAsyncContextManager

from kivy.graphics import Translate, Rectangle, Color, CanvasBase
from kivy.core.window import Window, WindowBase
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout


import asynckivy as ak
from asynckivy import anim_attrs_abbr as anim_attrs


DARK = (0., 0., 0., .8)
Transition: TypeAlias = Callable[[Widget, FloatLayout, WindowBase], AbstractAsyncContextManager]


@asynccontextmanager
async def no_transition(dialog: Widget, parent: FloatLayout, window: WindowBase):
    '''
    .. code-block::

        from asynckivy import modal

        async with modal.open(widget, transition=modal.no_transition):
            ...
    '''
    yield


class FadeTransition:
    '''
    .. code-block::

        from asynckivy import modal

        async with modal.open(widget, transition=modal.FadeTransition(...)):
            ...
    '''
    def __init__(self, *, in_duration=.1, out_duration=.1, background_color=DARK):
        self.in_duration = in_duration
        self.out_duration = out_duration
        self.background_color = background_color

    @asynccontextmanager
    async def __call__(self, dialog: Widget, parent: FloatLayout, window: WindowBase):
        parent_canvas = parent.canvas.before
        parent_canvas.add(bg_canvas := CanvasBase())
        try:
            parent.opacity = 0
            await ak.sleep(0)
            with bg_canvas:
                Color(*self.background_color)
                Rectangle(size=parent.size)
            await anim_attrs(parent, d=self.in_duration, opacity=1.0)
            yield
            await anim_attrs(parent, d=self.out_duration, opacity=0.0)
        finally:
            parent_canvas.remove(bg_canvas)


class SlideTransition:
    '''
    .. code-block::

        from asynckivy import modal

        async with modal.open(widget, transition=modal.SlideTransition(...)):
            ...
    '''
    def __init__(self, *, in_duration=.2, out_duration=.2, background_color=DARK,
                 in_curve='out_back', out_curve='in_back',
                 in_direction: Literal['left', 'right', 'down', 'up']='down',
                 out_direction: Literal['left', 'right', 'down', 'up']='up'):
        self.in_duration = in_duration
        self.out_duration = out_duration
        self.background_color = background_color
        self.in_curve = in_curve
        self.out_curve = out_curve
        self.in_direction = in_direction
        self.out_direction = out_direction

    @asynccontextmanager
    async def __call__(self, dialog: Widget, parent: FloatLayout, window: WindowBase):
        parent.opacity = 0.
        await ak.sleep(0)
        parent_canvas = parent.canvas.before
        parent_canvas.add(bg_canvas := CanvasBase())
        try:
            bg_alpha = self.background_color[3]
            with bg_canvas:
                bg_color = Color(*self.background_color[:3], 0.)
                Rectangle(size=parent.size)
            with ak.transform(dialog, use_outer_canvas=True) as ig:
                x_dist = y_dist = 0.
                match self.in_direction:
                    case 'down':
                        y_dist = parent.height - dialog.y
                    case 'up':
                        y_dist = -dialog.top
                    case 'left':
                        x_dist = parent.width - dialog.x
                    case 'right':
                        x_dist = -dialog.right
                    case _:
                        raise ValueError(f'Invalid in_direction: {self.in_direction}')
                ig.add(mat := Translate(x_dist, y_dist))
                parent.opacity = 1.
                await ak.wait_all(
                    anim_attrs(mat, d=self.in_duration, t=self.in_curve, x=0, y=0),
                    anim_attrs(bg_color, d=self.in_duration, a=bg_alpha),
                )
                yield
                x_dist = y_dist = 0.
                match self.out_direction:
                    case 'up':
                        y_dist = parent.height - dialog.y
                    case 'down':
                        y_dist = -dialog.top
                    case 'right':
                        x_dist = parent.width - dialog.x
                    case 'left':
                        x_dist = -dialog.right
                    case _:
                        raise ValueError(f'Invalid out_direction: {self.out_direction}')
                await ak.wait_all(
                    anim_attrs(mat, d=self.out_duration, t=self.out_curve, x=x_dist, y=y_dist),
                    anim_attrs(bg_color, d=self.out_duration, a=0.),
                )
        finally:
            parent_canvas.remove(bg_canvas)


def _dismiss_when_escape_key_or_back_button_is_pressed(dismiss, window, key, *args):
    '''Dismiss when the escape key or the Android back button is pressed.'''
    if key == 27:
        dismiss(cause='escape_key')
        return True
    elif key == 1073742106:  # https://github.com/kivy/kivy/issues/9075
        dismiss(cause='back_button')
        return True


class ParentOfModalDialog(FloatLayout):
    '''(internal)'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._block_inputs = True
        self.dismiss: Callable | None = None

    @contextmanager
    def accept_inputs(self):
        self._block_inputs = False
        try:
            yield
        finally:
            self._block_inputs = True

    def on_touch_down(self, touch):
        if self._block_inputs:
            return True
        dialog = self.children[0]
        # ParentOfModalDialog is not a relative-type widget, no need for translation
        if dialog.collide_point(*touch.opos):
            dialog.dispatch('on_touch_down', touch)
        elif (f := self.dismiss) is not None:
            f(cause='outside_touch')
        return True

    def on_touch_move(self, touch):
        if self._block_inputs:
            return True
        dialog = self.children[0]
        # ParentOfModalDialog is not a relative ...
        if dialog.collide_point(*touch.pos):
            dialog.dispatch('on_touch_move', touch)
        return True

    def on_touch_up(self, touch):
        if self._block_inputs:
            return True
        dialog = self.children[0]
        # ParentOfModalDialog is not a relative ...
        if dialog.collide_point(*touch.pos):
            dialog.dispatch('on_touch_up', touch)
        return True


@asynccontextmanager
async def open(
    dialog: Widget, *, window: WindowBase=Window, auto_dismiss=True,
    transition: Transition=FadeTransition(), _cache=[],
) -> AsyncIterator[ak.StatefulEvent]:
    '''
    Returns an async context manager that displays the given widget as a modal dialog.

    :param dialog: The widget to display as a dialog.
    :param window: The window in which to display the dialog.
    :param auto_dismiss: Whether to dismiss the dialog when the user touches outside it or presses
                         the escape key or the Android back button.
    :param transition: The transition effect to use when opening and dismissing the dialog.

    You can check whether the dialog was auto-dismissed and determine the cause as follows:

    .. code-block::

        async with open(dialog) as auto_dismiss_event:
            ...
        if auto_dismiss_event.is_fired:
            print("The dialog was auto-dismissed")

            # 'outside_touch', 'escape_key' or 'back_button'
            cause_of_dismissal = auto_dismiss_event.params[1]['cause']
    '''
    async with AsyncExitStack() as stack:
        defer = stack.callback

        parent = _cache.pop() if _cache else ParentOfModalDialog(); defer(_cache.append, parent)
        parent.dismiss = None
        parent.add_widget(dialog); defer(parent.remove_widget, dialog)
        window.add_widget(parent); defer(window.remove_widget, parent)

        await stack.enter_async_context(transition(dialog, parent, window))
        ad_event = ak.StatefulEvent()  # 'ad' stands for 'auto dismiss'
        if auto_dismiss:
            keyboard_handler = partial(_dismiss_when_escape_key_or_back_button_is_pressed, ad_event.fire)
            defer(window.unbind_uid, "on_keyboard", window.fbind("on_keyboard", keyboard_handler))
            parent.dismiss = ad_event.fire
            await stack.enter_async_context(ak.move_on_when(ad_event.wait()))
        with parent.accept_inputs():
            yield ad_event
