import itertools
from contextlib import nullcontext
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
import asynckivy as ak


async def switch_between_widgets(
    layout, out_widget, in_widget, *, relative=False, block_touch_events=True, clip_to_layout=False,
    transition,
):
    '''
    :param relative: Must be True if the layout is a relative-type widget, False otherwise.
    :param transition: The transition to use for switching between the widgets.
    :param block_touch_events: If True, touch events will be blocked during the transition.
    :param clip_to_layout: If True, drawing will be clipped to the layout's bounds during the transition.
    '''
    if out_widget.parent != layout:
        raise ValueError("out_widget must be a child of the layout")
    if in_widget.parent is not None:
        raise ValueError("in_widget must not have a parent")

    nc = nullcontext()
    with (
        ak.block_touch_events(layout) if block_touch_events else nc,
        ak.stencil_widget_mask(layout, canvas_layer="inner_outer", relative=relative) if clip_to_layout else nc
    ):
        async with transition(layout, canvas_layer="inner_outer"):
            child_idx = layout.children.index(out_widget)
            layout.remove_widget(out_widget)
            layout.add_widget(in_widget, index=child_idx)


KV_CODE = r'''
BoxLayout:
    orientation: 'vertical'
    padding: (dp(100), 0)  # Set a large padding so that clipping is easy to see.
    RelativeLayout:
        id: screen_manager
        size_hint_y: 3
    AnchorLayout:
        padding: '20dp'
        Button:
            id: btn
            size_hint: None, None
            size: self.texture_size
            padding: '20dp'
            text: 'switch screen'
            font_size: '20sp'
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        ak.managed_start(self.main())

    async def main(self):
        from asynckivy import transition as transition_module

        sm = self.root.ids.screen_manager
        btn = self.root.ids.btn
        screens = itertools.cycle((
            F.Label(text='Screen 1', font_size=64),
            F.Button(text='Screen 2', font_size=64),
        ))
        cur_screen = next(screens)
        sm.add_widget(cur_screen)
        while True:
            await ak.event(btn, 'on_release')
            next_screen = next(screens)
            await switch_between_widgets(
                sm, cur_screen, next_screen,
                relative=True, clip_to_layout=True,
                transition=partial(transition_module.slide, duration=0.6),
            )
            cur_screen = next_screen


if __name__ == '__main__':
    SampleApp().run()
