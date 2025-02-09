__all__ = ("managed_start", )

import asyncgui
from kivy.clock import Clock


async def _setup():
    global _global_nursery
    async with asyncgui.open_nursery() as nursery:
        _global_nursery = nursery
        await asyncgui.sleep_forever()


_global_nursery = None
_root_task = asyncgui.start(_setup())
managed_start = _global_nursery.start

__managed_start_doc__ = '''
A task started with this function will be automatically cancelled when an ``App.on_stop``
event fires, if it is still running. This prevents the task from being cancelled by the garbage
collector, ensuring more reliable cleanup. You should always use this function instead of calling
``asynckivy.start`` directly, except when writing unit tests.

.. code-block::

    task = managed_start(async_func(...))

.. versionadded:: 0.7.1
'''


def _schedule_teardown(dt):
    from kivy.app import App
    app = App.get_running_app()
    if app is None:
        return
    app.fbind("on_stop", lambda __: _root_task.cancel())


Clock.schedule_once(_schedule_teardown)
