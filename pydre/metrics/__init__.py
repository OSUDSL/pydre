#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations  # needed for python < 3.9

__all__ = ['common', 'driverdistraction']

import typing
from typing import List
from functools import partial, wraps

import logging
logger = logging.getLogger(__name__)

metricsList = {}
metricsColNames = {}

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

def registerMetric(name, function, columnnames: typing.Optional[List[str]] = None):
    metricsList[name] = function
    if columnnames:
        metricsColNames[name] = columnnames
    else:
        metricsColNames[name] = [name, ]
