__all__ = ('get_logger', )


import functools


@functools.lru_cache(maxsize=None)
def get_logger(name):
    from logging import getLogger, StreamHandler, WARNING
    logger = getLogger(name)
    logger.addHandler(StreamHandler(WARNING))
    return logger
