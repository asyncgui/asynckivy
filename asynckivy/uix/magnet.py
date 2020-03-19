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

    def on_children(self, *args):
        if len(self.children) > 1:
            raise ValueError('AKMagnet can have only one child')
        self._trigger_start_anim()

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
