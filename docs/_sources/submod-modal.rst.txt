==================
Modal (submodule)
==================

The ``asynckivy.modal`` submodule provides an easy way to display modal dialogs in Kivy applications.
Unlike :mod:`kivy.uix.modalview`:

* You can use any widget as a modal dialog. (:class:`~kivy.uix.modalview.ModalView` is not required.)
* Consequently, you have full control over the dialog's appearance and transitions.

.. code-block::

    from asynckivy import modal

    async with modal.open(any_widget):
        ...

If you leave the with-block empty, the dialog will be dismissed immediately — which is probably not what you want.
To keep it open, you must prevent the with-block from exiting. For example:

.. code-block::

    async with modal.open(any_widget):
        await ak.event(any_widget.ids.close_button, 'on_release')

A close button is not required for a dialog to work.
The user can still dismiss the dialog by touching outside of it, pressing the Escape key or pressing the Android back
button — unless ``auto_dismiss`` is set to ``False``.

.. code-block::

    # This is totally fine.
    async with modal.open(any_widget):
        await ak.sleep_forever()

    # This may not be fine, depending on the situation.
    async with modal.open(any_widget, auto_dismiss=False):
        await ak.sleep_forever()


API Reference
-------------

.. automodule:: asynckivy.modal
    :members:
    :undoc-members:
    :exclude-members:
