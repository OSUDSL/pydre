from loguru import logger
from typing import Optional, Callable, Concatenate

__all__ = ["common", "eyetracking", "gazeangle"]

from ..core import DriveData

filtersList: dict[
    str, Callable[Concatenate[DriveData, ...], DriveData]
] = {}


def registerFilter(filtername: Optional[str] = None) -> Callable:
    def registering_decorator(
        func: Callable[Concatenate[DriveData, ...], DriveData],
    ) -> Callable[Concatenate[DriveData, ...], DriveData]:
        name = filtername
        if not name:
            name = getattr(func, '__name__', repr(func))
        # register function
        filtersList[name] = func
        return func

    return registering_decorator
