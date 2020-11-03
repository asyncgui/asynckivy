__all__ = ('MotionEventAlreadyEndedError', )


class MotionEventAlreadyEndedError(Exception):
    """A MotionEvent that being waited for its updation/completion has
    already ended."""
