#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations # needed for python < 3.9

__all__ = ['common', 'driverdistraction']

metricsList = {}
metricsColNames = {}


def registerMetric(name, function, columnnames: str =None):
    metricsList[name] = function
    if columnnames:
        metricsColNames[name] = columnnames
    else:
        metricsColNames[name] = [name, ]


