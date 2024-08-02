import logging

logger = logging.getLogger(__name__)


__all__ = ["common"]

filtersList = {}
filtersColNames = {}


def registerFilter(jsonname=None, columnnames=None):
    def registering_decorator(func):
        jname = jsonname
        if not jname:
            jname = func.__name__
        # register function
        filtersList[jname] = func
        if columnnames:
            filtersColNames[jname] = columnnames
        else:
            filtersColNames[jname] = [
                jname,
            ]
        return func

    return registering_decorator


# filters defined here take a DriveData object and return an updated DriveData object
