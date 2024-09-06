from loguru import logger
from typing import Optional, Callable

__all__ = ["common", "eyetracking", "R2D"]

filtersList = {}
filtersColNames = {}

def registerFilter(filtername: Optional[str] =None, columnnames: Optional[list[str]]=None) -> Callable:
    def registering_decorator(func) -> Callable:
        name = filtername
        if not name:
            name = func.__name__
        # register function
        filtersList[name] = func
        if columnnames:
            filtersColNames[name] = columnnames
        else:
            filtersColNames[name] = [
                name,
            ]
        return func

    return registering_decorator
