__all__ = (
    'MotionEventAlreadyEndedError',
    'WouldBlock', 'ClosedResourceError', 'EndOfResource',
)
from asyncgui.exceptions import *  # noqa


class MotionEventAlreadyEndedError(Exception):
    """A MotionEvent has already ended."""


class WouldBlock(Exception):
    """(took from trio)
    Raised by X_nowait functions if X would block.
    """


class ClosedResourceError(Exception):
    """(took from trio)
    Raised when attempting to use a resource after it has been closed.
    """


class EndOfResource(Exception):
    """(similar to trio's EndOfChannel)
    This is analogous to an "end-of-file" condition, but for resources in general.
    """
