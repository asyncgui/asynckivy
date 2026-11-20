=========================
SceneSwitcher (submodule)
=========================

``sceneswitcher`` provides functionality similar to :class:`~kivy.uix.screenmanager.ScreenManager`, but in an async style.
You define each scene as an async generator function, and scene transitions are triggered by ``yield`` expressions inside the function.

.. code-block::

    async def scene(parent, userdata):
        setup()
        try:
            # The first yield is the signal that the scene is ready to be displayed.
            yield

            main_logic()

            # The second yield is the signal that the scene is done, and wants to be switched to another scene.
            yield next_scene, transition
        finally:
            teardown()

    async def next_scene(parent, userdata):
        ...

Because each scene is defined as a function, you can rely on the ``with`` statement for cleanup,
which is more flexible than the ``ScreenManager``'s lifecycle hooks (``on_enter``, ``on_leave``, ...).
The example below shows how ``ScreenManager``-style code can be translated into an async generator.

The ``ScreenManager`` style:

.. code-block:: yaml

    #:import sm kivy.uix.screenmanager

    <TitleScreen@Screen>:
        name: "title"
        on_pre_enter: print("on_pre_enter")
        on_enter: print("on_enter")
        on_pre_leave: print("on_pre_leave")
        on_leave: print("on_leave")
        BoxLayout:
            orientation: "vertical"
            Label:
                text: "Title"
            Button:
                text: "Start"
                on_release:
                    mgr = root.manager
                    mgr.transition = sm.FadeTransition()
                    mgr.current = "menu"

The async generator style:

.. code-block::

    from contextlib import ExitStack

    from kivy.lang import Builder
    import asynckivy as ak
    from asynckivy import transition

    TITLE_KV ="""
    BoxLayout:
        orientation: "vertical"
        Label:
            text: "Title"
        Button:
            id: start_btn
            text: "Start"
    """

    async def title_scene(parent, userdata, _cache=[]):
        with ExitStack() as stack:
            defer = stack.callback

            tree = _cache.pop() if _cache else Builder.load_string(TITLE_KV)
            defer(_cache.append, tree)
            parent.add_widget(tree)
            defer(parent.remove_widget, tree)
            defer(print, "on_leave")

            print("on_pre_enter")
            yield
            print("on_enter")

            await ak.event(tree.ids.start_btn, "on_release")

            print("on_pre_leave")
            yield menu_scene, transition.fade

The ``menu_scene`` argument may also be a string, in which case it is treated as a fully qualified import path:

.. code-block::

    from xxx.yyy import zzz
    yield zzz, transition

    # equivalent to the above
    yield "xxx.yyy.zzz", transition
