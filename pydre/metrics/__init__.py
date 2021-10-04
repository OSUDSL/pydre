#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations # needed for python < 3.9

__all__ = ['common', 'arriver', 'driverdistraction']

import pandas
import pydre.core
import numpy

import numpy as np
import math
import logging
import scipy
from scipy import signal


import ctypes

logger = logging.getLogger('PydreLogger')

metricsList = {}
metricsColNames = {}


def registerMetric(name, function, columnnames: str =None):
    metricsList[name] = function
    if columnnames:
        metricsColNames[name] = columnnames
    else:
        metricsColNames[name] = [name, ]


