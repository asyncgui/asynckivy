__all__ = ('transform', 'suppress_event', 'sync_attr', 'sync_attrs', )
import typing as T
from contextlib import contextmanager
from functools import partial

from kivy.event import EventDispatcher
from kivy.graphics import PushMatrix, PopMatrix, InstructionGroup


@contextmanager
def transform(widget, *, use_outer_canvas=False) -> T.ContextManager[InstructionGroup]:
    '''
    Returns a context manager that sandwiches the ``widget``'s existing canvas instructions between
    a :class:`kivy.graphics.PushMatrix` and a :class:`kivy.graphics.PopMatrix`, and inserts an
    :class:`kivy.graphics.InstructionGroup` right next to the ``PushMatrix``. Those three instructions will be removed
    when the context manager exits.

    This may be useful when you want to animate a widget.

    **Usage**

    .. code-block::

        from kivy.graphics import Rotate

        async def rotate_widget(widget, *, angle=360.):
            with transform(widget) as ig:  # <- InstructionGroup
                ig.add(rotate := Rotate(origin=widget.center))
                await anim_attrs(rotate, angle=angle)

    If the position or size of the ``widget`` changes during the animation, you might need :class:`sync_attr`.

    **The use_outer_canvas parameter**

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

    .. warning::

        You need to be careful when you suppress an ``on_touch_xxx`` event.
        See :ref:`kivys-event-system` for details.
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


class sync_attr:
    '''
    Creates one-directional binding between attributes.

    .. code-block::

        import types

        widget = Widget(x=100)
        obj = types.SimpleNamespace()

        sync_attr(from_=(widget, 'x'), to_=(obj, 'xx')):
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
