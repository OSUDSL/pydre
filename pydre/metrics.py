#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas

metricsList = {}

# metrics defined here take a list of pandas tables and return a single floating point value
def meanVelocity(regions, cutoff=0):
	total_vel = pandas.Series()
	for r in regions:
		total_vel = total_vel.append(r[r.Velocity >= cutoff].Velocity)
	return total_vel.mean()

metricsList['meanVelocity'] = meanVelocity
