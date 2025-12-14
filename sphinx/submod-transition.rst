======================
Transition (submodule)
======================

The ``asynckivy.transition`` submodule provides various transition effects for creating smooth visual
transitions for Kivy widgets. All APIs in this module are designed to be used with ``async with`` statements:

.. code-block::

    from asynckivy import transition

    async with transition.slide(widget):
        ...

You can imitate the behavior of the :class:`~kivy.uix.screenmanager.ScreenManager` by adding or removing widgets from
a layout inside the with-block:

.. code-block::

    from kivy.factory import Factory as F
    from asynckivy import transition

    layout = F.RelativeLayout()
    screen1 = F.Label(text='Screen 1')
    screen2 = F.Label(text='Screen 2')
    layout.add_widget(screen1)

    ...

    async with transition.slide(layout):
        layout.remove_widget(screen1)
        layout.add_widget(screen2)

Actually, ScreenManager does more than just transitions — it also blocks touch events during transitions
and clips its drawing area. To replicate those behaviors as well:

.. code-block::

    import asynckivy as ak

    with (
        ak.block_touch_events(layout),
        ak.stencil_widget_mask(layout, relative=True, working_layer="outer"),
    ):
        async with transition.slide(layout, working_layer="inner_outer"):
            layout.remove_widget(screen1)
            layout.add_widget(screen2)


API Reference
-------------

.. automodule:: asynckivy.transition
    :members:
    :undoc-members:
    :exclude-members:
