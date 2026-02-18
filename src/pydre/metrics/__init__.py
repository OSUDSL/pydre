__all__ = ["registerMetric", "common", "box", "driverdistraction", "gazeanglecutout"]

from functools import wraps
from typing import Any, Optional, Callable, Concatenate
from loguru import logger
from ..core import DriveData

metricsList: dict[str, Callable[Concatenate[DriveData, ...], Any]] = {}
metricsColNames: dict[str, list[str]] = {}


def registerMetric(
    metricname: Optional[str] = None, columnnames: Optional[list[str]] = None
) -> Callable:
    def registering_decorator(
        func: Callable[Concatenate[DriveData, ...], Any],
    ) -> Callable[Concatenate[DriveData, ...], Any]:
        name: str = metricname or getattr(func, '__name__', repr(func))
        # register function
        metricsList[name] = func
        if columnnames:
            metricsColNames[name] = columnnames
        else:
            metricsColNames[name] = [
                name,
            ]
        return func

    return registering_decorator


def check_data_columns(arg):
    def argwrapper(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            logger.debug(f"{f} was called with arguments={args} and kwargs={kwargs}")
            value = f(*args, **kwargs)
            logger.debug(f"{f} return value {value}")
            return value

        return wrapper

    return argwrapper
