#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations  # needed for python < 3.9

__all__ = ['common', 'driverdistraction']

import typing
from typing import List
import logging

metricsList = {}
metricsColNames = {}

def registerMetric(name, function, columnnames: typing.Optional[List[str]] = None):
    metricsList[name] = function
    if columnnames:
        metricsColNames[name] = columnnames
    else:
        metricsColNames[name] = [name, ]
