__all__ = ('AKDrawer', )

from kivy.properties import (
    NumericProperty, ColorProperty, OptionProperty, BooleanProperty,
)
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label

import asynckivy as ak

KV_CODE = '''
<AKDrawerTab>:
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
        PushMatrix:
        Rotate:
            origin: self.center
            angle: self.icon_angle
    canvas.after:
        PopMatrix:

<AKDrawer>:
    canvas.before:
        Color:
            rgba: root.background_color
        Rectangle:
            pos: 0, 0
            size: self.size
    AKDrawerTab:
        id: tab
        background_color: root.background_color
'''
Builder.load_string(KV_CODE)


class AKDrawerTab(ButtonBehavior, Label):
    background_color = ColorProperty()
    icon_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            import kivymd.font_definitions
            from kivymd.icon_definitions import md_icons
            self.font_name = 'Icons'
            self.text = md_icons['menu-right']
        except ImportError:
            self.text = '>'

    __ = {
        'l': {'x': 1, 'center_y': .5, },
        'r': {'right': 0, 'center_y': .5, },
        'b': {'y': 1, 'center_x': .5, },
        't': {'top': 0, 'center_x': .5, },
    }
    def update(self, anchor, *, __=__):
        from kivy.metrics import sp
        anchor = anchor[0]
        self.font_size = font_size = max(sp(15), 24)
        self.size = (font_size, font_size, )
        self.size_hint = (.4, None) if anchor in 'tb' else (None, .4)
        self.pos_hint = __[anchor]

    __ = None



class AKDrawer(RelativeLayout):
    '''(experimental)

    warning:

        This widget must be a child of `FloatLayout`.
        (including its subclasses e.g. `RelativeLayout` `Screen`)

        When you no longer need this widget, you must remove it from
        the parent, like this:

            drawer.parent.remove_widget(drawer)
        
        Otherwise, its internal coroutine would keep holding a reference
        to it, and prevent it from being garbage-collected.
    '''
    __events__ = ('on_pre_open', 'on_open', 'on_pre_close', 'on_close', )

    top_when_opened = BooleanProperty(False)
    '''If True, moves myself on top of the other siblings when opened.'''

    duration = NumericProperty(.3)
    '''Duration of the opening/closing animations.'''

    background_color = ColorProperty("#222222")

    anchor = OptionProperty(
        'lm', options=r'lt lm lb rt rm rb bl bm br tl tm tr'.split())
    '''Specifies where myself is attached to.

        'l' stands for 'left'.
        'r' stands for 'right'.
        't' stands for 'top'.
        'b' stands for 'bottom'.
        'm' stands for 'middle'.
    '''

    def __init__(self, **kwargs):
        self._coro = None
        self._is_moving_to_the_top = False
        self._trigger_reset = trigger = Clock.create_trigger(self.reset, 0)
        super().__init__(**kwargs)
        self.fbind('anchor', trigger)
        trigger()

    def on_parent(self, __, parent):
        if parent and (not isinstance(parent, FloatLayout)):
            raise ValueError("AKDrawer needs to be a child of FloatLayout!!")
        if self._is_moving_to_the_top:
            return
        self._trigger_reset()

    def reset(self, *args, **kwargs):
        if self._coro is not None:
            self._coro.close()
            self._coro = None
        if self.parent is None:
            return
        self._coro = self._main()
        ak.start(self._coro)

    async def _main(self):
        anchor = self.anchor
        moves_vertically = anchor[0] in 'tb'
        moves_forward_direction = anchor[0] in 'lb'
        parent = self.parent
        tab = self.ids.tab.__self__
        tab.update(anchor)
        self.pos_hint = ph = _get_initial_pos_hint_from_anchor(anchor)
        # '_c'-suffix means 'close'.  '_o'-suffix means 'open'.
        icon_angle_c = _get_initial_icon_angle_from_anchor(anchor)
        icon_angle_o = icon_angle_c + 180.
        pos_key_c = _anchor2propname_opposite(anchor)
        pos_key_o = _anchor2propname(anchor)
        ph_value = 0. if moves_forward_direction else 1.

        tab.icon_angle = icon_angle_c
        ph[pos_key_c] = ph_value
        while True:
            await ak.event(tab, 'on_press')
            self.dispatch('on_pre_open')
            if self.top_when_opened:
                self._is_moving_to_the_top = True
                parent.remove_widget(self)
                parent.add_widget(self)
                self._is_moving_to_the_top = False
            del ph[pos_key_c]
            pos_value = getattr(parent, pos_key_o)
            pos_value = parent.to_local(pos_value, pos_value)[moves_vertically]
            await ak.animate(self, d=self.duration, **{pos_key_o: pos_value})
            await ak.animate(tab, d=self.duration, icon_angle=icon_angle_o)
            ph[pos_key_o] = ph_value
            self.dispatch('on_open')
            await ak.event(tab, 'on_press')
            self.dispatch('on_pre_close')
            del ph[pos_key_o]
            pos_value = getattr(parent, pos_key_o)
            pos_value = parent.to_local(pos_value, pos_value)[moves_vertically]
            await ak.animate(self, d=self.duration, **{pos_key_c: pos_value})
            await ak.animate(tab, d=self.duration, icon_angle=icon_angle_c)
            ph[pos_key_c] = ph_value
            self.dispatch('on_close')

    def on_pre_open(self):
        pass

    def on_open(self):
        pass

    def on_pre_close(self):
        pass

    def on_close(self):
        pass


__ = {'l': 'x', 't': 'top', 'r': 'right', 'b': 'y', }
def _anchor2propname(anchor, *, __=__):
    return __[anchor[0]]


__ = {'l': 'right', 't': 'y', 'r': 'x', 'b': 'top', }
def _anchor2propname_opposite(anchor, *, __=__):
    return __[anchor[0]]


__ = {
    'bl': {'x': 0., },
    'tl': {'x': 0., },
    'lb': {'y': 0., },
    'rb': {'y': 0., },
    'bm': {'center_x': .5, },
    'tm': {'center_x': .5, },
    'rm': {'center_y': .5, },
    'lm': {'center_y': .5, },
    'br': {'right': 1., },
    'tr': {'right': 1., },
    'lt': {'top': 1., },
    'rt': {'top': 1., },
}
def _get_initial_pos_hint_from_anchor(anchor, *, __=__):
    return __[anchor].copy()


__ = {'l': 0., 't': 270., 'r': 180., 'b': 90., }
def _get_initial_icon_angle_from_anchor(anchor, *, __=__):
    return __[anchor[0]]


__ = None
