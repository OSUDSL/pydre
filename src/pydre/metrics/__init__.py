__all__ = ["common", "box", "driverdistraction"]

from functools import wraps
from typing import Optional, Callable

from loguru import logger

metricsList = {}
metricsColNames = {}


def registerMetric(
    metricname: Optional[str] = None, columnnames: Optional[list[str]] = None
) -> Callable:
    def registering_decorator(func: Callable) -> Callable:
        name = metricname
        if not metricname:
            name = func.__name__
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