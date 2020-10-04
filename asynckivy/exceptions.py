'''Took from asyncio'''


__all__ = ('CancelledError', 'InvalidStateError', )


class CancelledError(BaseException):
    """The Task was cancelled."""


class InvalidStateError(Exception):
    """The operation is not allowed in the current state."""
