import typing as T
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from functools import partial

from kivy.event import EventDispatcher
from kivy.graphics import (
    PushMatrix, PopMatrix, InstructionGroup, StencilPush, StencilUse, StencilUnUse, StencilPop, Rectangle,
    Canvas, Instruction,
)
CanvasLayer: T.TypeAlias = T.Literal["inner", "outer", "inner_outer"]


@contextmanager
def sandwich_canvas(target: Canvas, top_bun: Instruction, bottom_bun: Instruction,
                    *, insertion_layer: CanvasLayer="inner"):
    '''
    Returns a context manager that sandwiches the ``target``'s graphics instructions between the
    ``top_bun`` and ``bottom_bun``.

    .. code-block::

        # The text of this label is drawn 20 pixels to the right of its original position.
        with sandwich_canvas(label.canvas, Translate(20, 0), Translate(-20, 0)):
            ...

    The ``insertion_layer`` parameter controls where ``top_bun`` and ``bottom_bun`` are inserted within the target
    canvas. If set to "inner" (the default), they are inserted into the **outer side** of the **inner** canvas:

    .. code-block:: yaml

        # ... represents existing instructions

        Widget:
            canvas.before:
                ...
            canvas:
                top_bun
                ...
                bottom_bun
            canvas.after:
                ...

    If set to "outer", they are inserted into the **outer side** of the **outer** canvas:

    .. code-block:: yaml

        Widget:
            canvas.before:
                top_bun
                ...
            canvas:
                ...
            canvas.after:
                ...
                bottom_bun

    If set to "inner_outer", they are inserted into the **inner side** of the **outer** canvas:

    .. code-block:: yaml

        Widget:
            canvas.before:
                ...
                top_bun
            canvas:
                ...
            canvas.after:
                bottom_bun
                ...

    .. versionadded:: 0.10.0
    '''
    c = target
    if insertion_layer == "inner":
        c.insert(1 if c.has_before else 0, top_bun)
        c.add(bottom_bun)
        before = after = c
    else:
        before = c.before
        after = c.after
        if insertion_layer == "outer":
            before.insert(0, top_bun)
            after.add(bottom_bun)
        else:  # inner_outer
            before.add(top_bun)
            after.insert(0, bottom_bun)
    try:
        yield
    finally:
        after.remove(bottom_bun)
        before.remove(top_bun)


@contextmanager
def transform(widget, *, working_layer: CanvasLayer="inner") -> Iterator[InstructionGroup]:
    '''
    Returns a context manager that helps apply transformations to the given widget.

    .. code-block::

        from kivy.graphics import Rotate

        async def rotate_widget(widget, *, angle=360.):
            with transform(widget) as ig:  # <- InstructionGroup
                ig.add(rotate := Rotate(origin=widget.center))
                await anim_attrs(rotate, angle=angle)

    :param working_layer: Controls which part of the widget's canvas is affected by the transformation.
        See :func:`sandwich_canvas` for details.

    .. versionchanged:: 0.10.0
        The ``use_outer_canvas`` parameter was replaced with the ``working_layer`` parameter.
    '''

    top_bun = InstructionGroup()
    top_bun.add(PushMatrix())
    top_bun.add(user_space := InstructionGroup())
    bottom_bun = PopMatrix()
    with sandwich_canvas(widget.canvas, top_bun, bottom_bun, insertion_layer=working_layer):
        yield user_space


class sync_attr:
    '''
    Creates one-directional binding between attributes.

    .. code-block::

        import types

        widget = Widget(x=100)
        obj = types.SimpleNamespace()

        sync_attr(from_=(widget, 'x'), to_=(obj, 'xx'))
        assert obj.xx == 100  # synchronized
        widget.x = 10
        assert obj.xx == 10  # synchronized
        obj.xx = 20
        assert widget.x == 10  # but not the other way around

    To make its effect temporary, use it with a with-statement:

    .. code-block::

        # The effect lasts only within the with-block.
        with sync_attr(...):
            ...

    This can be particularly useful when combined with :func:`transform`.

    .. code-block::

        from kivy.graphics import Rotate

        async def rotate_widget(widget, *, angle=360.):
            rotate = Rotate()
            with (
                transform(widget) as ig,
                sync_attr(from_=(widget, 'center'), to_=(rotate, 'origin')),
            ):
                ig.add(rotate)
                await anim_attrs(rotate, angle=angle)

    .. versionadded:: 0.6.1

    .. versionchanged:: 0.8.0
        The context manager now applies its effect upon creation, rather than when its ``__enter__()`` method is
        called, and ``__enter__()`` no longer performs any action.

        Additionally, the context manager now assigns the ``from_`` value to the ``to_`` upon creation:

        .. code-block::

            with sync_attr((widget, 'x'), (obj, 'xx')):
                assert widget.x == obj.xx
    '''
    __slots__ = ("__exit__", )

    def __init__(self, from_: tuple[EventDispatcher, str], to_: tuple[T.Any, str]):
        setattr(*to_, getattr(*from_))
        bind_uid = from_[0].fbind(from_[1], partial(self._sync, setattr, *to_))
        self.__exit__ = partial(self._unbind, *from_, bind_uid)

    @staticmethod
    def _sync(setattr, obj, attr_name, event_dispatcher, new_value):
        setattr(obj, attr_name, new_value)

    @staticmethod
    def _unbind(event_dispatcher, event_name, bind_uid, *__):
        event_dispatcher.unbind_uid(event_name, bind_uid)

    def __enter__(self):
        pass


class sync_attrs:
    '''
    When multiple :class:`sync_attr` calls take the same ``from_`` argument, they can be merged into a single
    :class:`sync_attrs` call. For instance, the following code:

    .. code-block::

        with sync_attr((widget, 'x'), (obj1, 'x')), sync_attr((widget, 'x'), (obj2, 'xx')):
            ...

    can be replaced with the following one:

    .. code-block::

        with sync_attrs((widget, 'x'), (obj1, 'x'), (obj2, 'xx')):
            ...

    This can be particularly useful when combined with :func:`transform`.

    .. code-block::

        from kivy.graphics import Rotate, Scale

        async def scale_and_rotate_widget(widget, *, scale=2.0, angle=360.):
            rotate = Rotate()
            scale = Scale()
            with (
                transform(widget) as ig,
                sync_attrs((widget, 'center'), (rotate, 'origin'), (scale, 'origin')),
            ):
                ig.add(rotate)
                ig.add(scale)
                await wait_all(
                    anim_attrs(rotate, angle=angle),
                    anim_attrs(scale, x=scale, y=scale),
                )

    .. versionadded:: 0.6.1

    .. versionchanged:: 0.8.0
        The context manager now applies its effect upon creation, rather than when its ``__enter__()`` method is
        called, and ``__enter__()`` no longer performs any action.

        Additionally, the context manager now assigns the ``from_`` value to the ``to_`` upon creation:

        .. code-block::

            with sync_attrs((widget, 'x'), (obj, 'xx')):
                assert widget.x is obj.xx
    '''
    __slots__ = ("__exit__", )

    def __init__(self, from_: tuple[EventDispatcher, str], *to_):
        sync = partial(self._sync, setattr, to_)
        sync(None, getattr(*from_))
        bind_uid = from_[0].fbind(from_[1], sync)
        self.__exit__ = partial(self._unbind, *from_, bind_uid)

    @staticmethod
    def _sync(setattr, to_, event_dispatcher, new_value):
        for obj, attr_name in to_:
            setattr(obj, attr_name, new_value)

    _unbind = staticmethod(sync_attr._unbind)

    def __enter__(self):
        pass


@contextmanager
def stencil_mask(widget, *, use_outer_canvas=False) -> Iterator[InstructionGroup]:
    '''
    Returns a context manager that allows restricting the drawing area of a specified widget to an arbitrary shape.

    .. code-block::

        with stencil_mask(widget) as drawable_area:
            ...

    The most common use case would be to confine drawing to the widget's own area,
    which can be achieved as follows:

    .. code-block::

        from kivy.graphics import Rectangle
        import asynckivy as ak

        rect = Rectangle()
        with (
            ak.sync_attr(from_=(widget, 'pos'), to_=(rect, 'pos')),  # A
            ak.sync_attr(from_=(widget, 'size'), to_=(rect, 'size')),
            ak.stencil_mask(widget) as drawable_area,
        ):
            drawable_area.add(rect)
            ...

    Note that if the ``widget`` is a relative-type widget and the ``use_outer_canvas`` parameter is
    False (the default), line A above must be removed.

    Since this use case is so common, :func:`stencil_widget_mask` is provided as a shorthand.

    .. versionadded:: 0.9.1
    '''
    IG = InstructionGroup
    shared_part = IG()
    first_group = IG()
    first_group.add(StencilPush())
    first_group.add(shared_part)
    first_group.add(StencilUse())
    last_group = IG()
    last_group.add(StencilUnUse())
    last_group.add(shared_part)
    last_group.add(StencilPop())

    c = widget.canvas
    first_group_idx = 0
    if use_outer_canvas:
        before = c.before
        after = c.after
    else:
        before = after = c
        if c.has_before:
            first_group_idx = 1

    before.insert(first_group_idx, first_group)
    after.add(last_group)
    try:
        yield shared_part
    finally:
        before.remove(first_group)
        after.remove(last_group)


@contextmanager
def stencil_widget_mask(widget, *, use_outer_canvas=False, relative=False) -> Iterator[InstructionGroup]:
    '''
    Returns a context manager that restricts the drawing area to the widget's own area.

    .. code-block::

        with stencil_widget_mask(widget):
            ...

    :param relative: Must be set to True if the ``widget`` is a relative-type widget.

    .. versionadded:: 0.9.1
    '''
    rect = Rectangle()
    with (
        sync_attr((widget, 'pos'), (rect, 'pos')) if use_outer_canvas or (not relative) else nullcontext(),
        sync_attr((widget, 'size'), (rect, 'size')),
        stencil_mask(widget, use_outer_canvas=use_outer_canvas) as drawable_area,
    ):
        drawable_area.add(rect)
        yield drawable_area
