logger = logging.getLogger('PydreLogger')


# filters defined here take a list of DriveData objects and return a ______________






filtersList = {}
filtersColNames = {}


def registerFilter(name, function, columnnames=None):
    filtersList[name] = function
    if columnnames:
        filtersColNames[name] = columnnames
    else:
        filtersColNames[name] = [name, ]