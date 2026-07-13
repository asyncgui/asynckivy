======================
Transition (submodule)
======================

The ``asynckivy.transition`` submodule provides various transition effects for creating smooth visual
transitions for Kivy widgets.

.. code-block::

    from asynckivy import transition

    async with transition.slide(label):
        label.text = "new text"

You can recreate the :class:`~kivy.uix.screenmanager.ScreenManager` by adding or removing widgets from
a layout inside the with-block:

.. code-block::

    from asynckivy import transition

    async def switch_between_widgets(layout, out_child, in_child):
        async with transition.slide(layout):
            child_idx = layout.children.index(out_child)
            layout.remove_widget(out_child)
            layout.add_widget(in_child, index=child_idx)

Actually, ScreenManager does more than just transitions — it also blocks touch events during transitions
and clips its drawing area. To recreate those behaviors as well:

.. code-block::

    import asynckivy as ak

    async def switch_between_widgets(layout, out_child, in_child):
        with (
            ak.block_touch_events(layout),
            ak.stencil_widget_mask(layout, canvas_layer="inner_outer"),
        ):
            child_idx = layout.children.index(out_child)
            async with transition.slide(layout, canvas_layer="inner_outer"):
                layout.remove_widget(out_child)
                layout.add_widget(in_child, index=child_idx)

We are not done yet, as this only works for non-relative layouts.
See ``recreating_the_screen_manager.py`` for a complete example.

API Reference
-------------

.. automodule:: asynckivy.transition
    :members:
    :undoc-members:
    :exclude-members:
