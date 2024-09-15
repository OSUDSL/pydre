from loguru import logger
from typing import Optional, Callable

__all__ = ["common", "eyetracking", "R2D"]

import pydre.core

filtersList = {}
filtersColNames = {}


def registerFilter(filtername: Optional[str] = None) -> Callable:
    def registering_decorator(
        func: Callable[[pydre.core.DriveData, ...], pydre.core.DriveData],
    ) -> Callable[[pydre.core.DriveData, ...], pydre.core.DriveData]:
        name = filtername
        if not name:
            name = func.__name__
        # register function
        filtersList[name] = func
        return func

    return registering_decorator
