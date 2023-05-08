 #!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations  # needed for python < 3.9

__all__ = ['common', 'box', 'driverdistraction']

import typing
from typing import List
from functools import partial, wraps

import logging
logger = logging.getLogger(__name__)

metricsList = {}
metricsColNames = {}

def registerMetric(jsonname=None, columnnames=None):
    def registering_decorator(func):
        jname = jsonname
        if not jname:
            jname = func.__name__
        # register function
        metricsList[jname] = func
        if columnnames:
            metricsColNames[jname] = columnnames
        else:
            metricsColNames[jname] = [jname, ]
        return func
    return registering_decorator

def check_data_columns(arg):
    def argwrapper(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            logger.debug(f'{f} was called with arguments={args} and kwargs={kwargs}')
            value = f(*args, **kwargs)
            logger.debug(f'{f} return value {value}')
            return value
        return wrapper
    return argwrapper
