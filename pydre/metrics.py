#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas
import pydre.core

metricsList = {}

# metrics defined here take a list of DriveData objects and return a single floating point value
def meanVelocity(regions, cutoff=0):
	total_vel = pandas.Series()
	for r in regions:
		data = r.data
		total_vel = total_vel.append(data[data.Velocity >= cutoff].Velocity)
	return total_vel.mean()

metricsList['meanVelocity'] = meanVelocity
