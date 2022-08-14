__all__ = ('transform', )
from contextlib import contextmanager

from kivy.graphics import PushMatrix, PopMatrix, InstructionGroup


@contextmanager
def transform(widget, *, use_outer_canvas=False):
    '''Return a context manager that sandwiches the widget's existing canvas instructions between PushMatrix and
    PopMatrix, and inserts an InstructionGroup right next to the PushMatrix. This may be useful when you want to
    animate a widget for a short period of time.

    Usage
    -----

    .. code-block:: python

        from kivy.graphics import Rotate

        async def rotate_widget(widget, *, angle=360.):
            with transform(widget) as ig:  # <- InstructionGroup
                ig.add(rotate := Rotate(origin=widget.center))
                await asynckivy.animate(rotate, angle=angle)

    The ``use_outer_canvas`` argument
    ---------------------------------

    While the context manager is active, the canvas of the widget would be:

    .. code-block:: yaml

        # ... represents existing instructions

        Widget:
            canvas.before:
                ...
            canvas:
                PushMatrix:
                InstructionGroup:
                ...
                PopMatrix:
            canvas.after:
                ...

    but if ``use_outer_canvas`` is True, it would be:

    .. code-block:: yaml

        Widget:
            canvas.before:
                PushMatrix:
                InstructionGroup:
                ...
            canvas:
                ...
            canvas.after:
                ...
                PopMatrix:
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
