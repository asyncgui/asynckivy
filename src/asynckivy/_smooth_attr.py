__all__ = ("smooth_attr", )
import typing as T
from functools import partial
import math

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy import properties as P
NUMERIC_TYPES = (P.NumericProperty, P.BoundedNumericProperty, )
SEQUENCE_TYPES = (P.ColorProperty, P.ReferenceListProperty, P.ListProperty, )


class smooth_attr:
    '''
    Makes an attribute smoothly follow another.

    .. code-block::

        import types

        widget = Widget(x=0)
        obj = types.SimpleNamespace(xx=100)

        # 'obj.xx' will smoothly follow 'widget.x'.
        smooth_attr(target=(widget, 'x'), follower=(obj, 'xx'))

    To make its effect temporary, use it with a with-statement:

    .. code-block::

        # The effect lasts only within the with-block.
        with smooth_attr(...):
            ...

    A key feature of this API is that if the target value changes while being followed,
    the follower automatically adjusts to the new value.

    :param target: Must be a numeric or numeric sequence type property, that is, one of the following:

        * :class:`~kivy.properties.NumericProperty`
        * :class:`~kivy.properties.BoundedNumericProperty`
        * :class:`~kivy.properties.ReferenceListProperty`
        * :class:`~kivy.properties.ListProperty`
        * :class:`~kivy.properties.ColorProperty`

    :param speed: The speed coefficient for following. A larger value results in faster following.
    :param min_diff: If the difference between the target and the follower is less than this value,
        the follower will instantly jump to the target's value. When the target is a ``ColorProperty``,
        you most likely want to set this to a very small value, such as ``0.01``. Defaults to ``dp(2)``.

    .. versionadded:: 0.8.0
    '''
    __slots__ = ("__exit__", )

    def __init__(self, target: tuple[EventDispatcher, str], follower: tuple[T.Any, str],
                 *, speed=10.0, min_diff=dp(2)):
        target_obj, target_attr = target
        target_desc = target_obj.property(target_attr)
        if isinstance(target_desc, NUMERIC_TYPES):
            update = self._update_follower
        elif isinstance(target_desc, SEQUENCE_TYPES):
            update = self._update_follower_ver_seq
        else:
            raise ValueError(f"Unsupported target type: {target_desc}")
        trigger = Clock.schedule_interval(
            partial(update, *target, *follower, -speed, -min_diff, min_diff), 0
        )
        bind_uid = target_obj.fbind(target_attr, trigger)
        self.__exit__ = partial(self._cleanup, trigger, target_obj, target_attr, bind_uid)

    @staticmethod
    def _cleanup(trigger, target_obj, target_attr, bind_uid, *__):
        trigger.cancel()
        target_obj.unbind_uid(target_attr, bind_uid)

    def __enter__(self):
        pass

    def _update_follower(getattr, setattr, math_exp, target_obj, target_attr, follower_obj, follower_attr,
                         negative_speed, min, max, dt):
        t_value = getattr(target_obj, target_attr)
        f_value = getattr(follower_obj, follower_attr)
        diff = f_value - t_value

        if min < diff < max:
            setattr(follower_obj, follower_attr, t_value)
            return False

        new_value = t_value + math_exp(negative_speed * dt) * diff
        setattr(follower_obj, follower_attr, new_value)

    _update_follower = partial(_update_follower, getattr, setattr, math.exp)

    def _update_follower_ver_seq(getattr, setattr, math_exp, zip, target_obj, target_attr,
                                 follower_obj, follower_attr, negative_speed, min, max, dt):
        t_value = getattr(target_obj, target_attr)
        f_value = getattr(follower_obj, follower_attr)
        p = math_exp(negative_speed * dt)
        still_going = False
        new_value = [
            (t_elem + p * diff) if (
                diff := f_elem - t_elem,
                _still_going := (diff <= min or max <= diff),
                still_going := (still_going or _still_going),
            ) and _still_going else t_elem
            for t_elem, f_elem in zip(t_value, f_value)
        ]
        setattr(follower_obj, follower_attr, new_value)
        return still_going

    _update_follower_ver_seq = partial(_update_follower_ver_seq, getattr, setattr, math.exp, zip)
