__all__ = ('transform', )
import typing as T
from contextlib import contextmanager

from kivy.graphics import PushMatrix, PopMatrix, InstructionGroup


@contextmanager
def transform(widget, *, use_outer_canvas=False) -> T.ContextManager[InstructionGroup]:
    '''
    Return a context manager that sandwiches the ``widget``'s existing canvas instructions between
    a :class:`kivy.graphics.PushMatrix` and a :class:`kivy.graphics.PopMatrix`, and inserts an
    :class:`kivy.graphics.InstructionGroup` right next to the ``PushMatrix``. Those three instructions are removed
    when the context manager exits.

    This may be useful when you want to animate a widget for a short period of time.

    **Usage**

    .. code-block::

        from kivy.graphics import Rotate

        async def rotate_widget(widget, *, angle=360.):
            with transform(widget) as ig:  # <- InstructionGroup
                ig.add(rotate := Rotate(origin=widget.center))
                await animate(rotate, angle=angle)

    If you want to animate for a long time, you might need extra work because you might have to prepare for the
    transition of some of widget's properties during the animation. In the above example it's the ``widget.center``,
    and here is an example of how to do it.

    .. code-block::
        :emphasize-lines: 4-5, 7-13, 18

        from contextlib import contextmanager
        from kivy.graphics import Rotate

        def _setter(obj, attr_name, event_dispatcher, prop_value):
            setattr(obj, attr_name, prop_value)

        @contextmanager
        def tmp_bind(event_dispatcher, prop_name, obj, attr_name):
            uid = event_dispatcher.fbind(prop_name, _setter, obj, attr_name)
            try:
                yield
            finally:
                ed.unbind_uid(prop_name, uid)

        async def rotate_widget(widget, *, angle=360.):
            with transform(widget) as ig:  # <- InstructionGroup
                ig.add(rotate := Rotate(origin=widget.center))
                with tmp_bind(widget, 'center', rotate, 'origin'):
                    await animate(rotate, angle=angle)

    **The** ``use_outer_canvas`` **parameter**

    While the context manager is active, the content of the widget's canvas would be:

    .. code-block:: yaml

        # ... represents existing instructions

        Widget:
            canvas.before:
                ...
            canvas:
                PushMatrix
                InstructionGroup
                ...
                PopMatrix
            canvas.after:
                ...

    but if ``use_outer_canvas`` is True, it would be:

    .. code-block:: yaml

        Widget:
            canvas.before:
                PushMatrix
                InstructionGroup
                ...
            canvas:
                ...
            canvas.after:
                ...
                PopMatrix
    '''

    c = widget.canvas
    if use_outer_canvas:
        before = c.before
        after = c.after
        push_mat_idx = 0
        ig_idx = 1
    else:
        c.before  # ensure 'canvas.before' exists

        # Index starts from 1 because 'canvas.before' is sitting at index 0 and we usually want it to remain first.
        # See https://github.com/kivy/kivy/issues/7945 for details.
        push_mat_idx = 1
        ig_idx = 2
        before = after = c

    push_mat = PushMatrix()
    ig = InstructionGroup()
    pop_mat = PopMatrix()

    before.insert(push_mat_idx, push_mat)
    before.insert(ig_idx, ig)
    after.add(pop_mat)
    try:
        yield ig
    finally:
        after.remove(pop_mat)
        before.remove(ig)
        before.remove(push_mat)
