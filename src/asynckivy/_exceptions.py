__all__ = (
    'MotionEventAlreadyEndedError',
)


class MotionEventAlreadyEndedError(Exception):
    '''
    This error occurs when an already ended touch is passed to an asynckivy's api that expects an ongoing touch.
    For instance:

    .. code-block::
        :emphasize-lines: 4

        import asynckivy as ak

        class MyWidget(Widget):
            def on_touch_up(self, touch):  # not 'on_touch_down'
                ak.start(self.handle_touch(touch))
                return True

            async def handle_touch(self, touch):
                try:
                    async for __ in ak.rest_of_touch_events(widget, touch):
                        ...
                except ak.MotionEventAlreadyEndedError:
                    ...
    '''
