AsyncKivy
=========

``asynckivy`` is an async library that saves you from ugly callback-style code,
like most of async libraries do.
Let's say you want to do:

#. ``print('A')``
#. wait for 1sec
#. ``print('B')```
#. wait for a button to be pressed
#. ``print('C')``

in that order.
Your code would look like this:

.. code-block::

   from kivy.clock import Clock

   def what_you_want_to_do(button):
      print('A')

      def one_sec_later(__):
         print('B')
         button.bind(on_press=on_button_press)
      Clock.schedule_once(one_sec_later, 1)

      def on_button_press(button):
         button.unbind(on_press=on_button_press)
         print('C')

   what_you_want_to_do(...)

It's not easy to understand.
If you use ``asynckivy``, the code above will become:

.. code-block::

   import asynckivy as ak

   async def what_you_want_to_do(button):
      print('A')
      await ak.sleep(1)
      print('B')
      await ak.event(button, 'on_press')
      print('C')

   ak.managed_start(what_you_want_to_do(...))

You may also want to read the ``asyncgui``'s documentation as it is the foundation of this library.

.. toctree::
   :hidden:

   notes
   notes-ja
   reference

* https://github.com/asyncgui/asyncgui
* https://github.com/asyncgui/asynckivy
