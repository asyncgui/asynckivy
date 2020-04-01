'''
Equivalent to
https://github.com/kivy-garden/garden.magnet
'''
__all__ = ('AKMagnet', )

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ListProperty
from asynckivy import start as ak_start, animate as ak_animate

class AKMagnet(Widget):
    duration = NumericProperty(1)
    transition = StringProperty('out_quad')
    anim_props = ListProperty(['pos', 'size', ])

    def __init__(self, **kwargs):
        self._props_watching = {}
        self._trigger_start_anim = \
            Clock.create_trigger(self._start_anim, -1)
        self._coro = None
        super().__init__(**kwargs)

    def on_kv_post(self, *args, **kwargs):
        self.bind(anim_props=self._on_anim_props)
        self.property('anim_props').dispatch(self)

    def _on_anim_props(self, __, anim_props):
        for prop, uid in self._props_watching.items():
            self.unbind_uid(prop, uid)
        self._props_watching = {
            prop: self.fbind(prop, self._trigger_start_anim)
            for prop in anim_props
        }

    def add_widget(self, widget, *args, **kwargs):
        if self.children:
            raise ValueError('AKMagnet can have only one child')
        widget.size = self.size
        widget.pos = self.pos
        return super().add_widget(widget, *args, **kwargs)

    def _start_anim(self, *args):
        if self._coro is not None:
            self._coro.close()
        if self.children:
            coro = ak_animate(
                self.children[0],
                d=self.duration,
                t=self.transition,
                **{prop: getattr(self, prop) for prop in self.anim_props}
            )
            ak_start(coro)
            self._coro = coro

    def disappear(self):
        '''(experimental)
        Silently disappears without ruining the layout.
        '''
        child = self.children[0]
        self.remove_widget(child)
        for name in _name_of_the_properties_need_to_be_copied:
            setattr(child, name, getattr(self, name))
        parent = self.parent
        if parent:
            index = parent.children.index(self)
            parent.remove_widget(self)
            parent.add_widget(child, index=index)


_name_of_the_properties_need_to_be_copied = (
    'size', 'pos', 'pos_hint', 'size_hint', 'size_hint_min', 'size_hint_max',
)
