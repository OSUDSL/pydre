#!/usr/bin/python
# -*- coding: utf-8 -*-


# metrics defined here take a list of pandas tables and return a single floating point value

def meanVelocity(regions, cutoff=0):
	sum_means = 0
	for r in regions:
		sum_means += r[r.Velocity >= cutoff].Velocity.mean()
	return sum_means


