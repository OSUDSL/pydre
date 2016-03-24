#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas
import pydre.core
import numpy
import math
import logging
logger = logging.getLogger(__name__)


# metrics defined here take a list of DriveData objects and return a single floating point value
def meanVelocity(drivedata: pydre.core.DriveData, cutoff=0):
	total_vel = pandas.Series()
	for d in drivedata.data:
		total_vel = total_vel.append(d[d.Velocity >= cutoff].Velocity)
	return total_vel.mean()


def steeringEntropy(drivedata: pydre.core.DriveData, cutoff=0):
	out = []
	for d in drivedata.data:
		if(len(d) > 0):
			df = pandas.DataFrame(d, columns=("SimTime", "Steer"))  # drop other columns
			df = pandas.DataFrame.drop_duplicates(df.dropna(axis=[0, 1], how='any'))  # remove nans and drop duplicates

			# resample data
			minTime = df.SimTime.values.min()
			maxTime = df.SimTime.values.max()
			nsteps = math.floor((maxTime - minTime) / 0.0167)  # divide into 0.0167s increments
			regTime = numpy.linspace(minTime, maxTime, num=nsteps)
			rsSteer = numpy.interp(regTime, df.SimTime, df.Steer)
			resampdf = numpy.column_stack((regTime, rsSteer))
			resampdf = pandas.DataFrame(resampdf, columns=("simTime", "rsSteerAngle"))

			# calculate predicted angle
			pAngle = (2.5 * df.Steer.values[3:, ]) - (2 * df.Steer.values[2:-1, ]) - (0.5 * df.Steer.values[1:-2, ])

			# calculate error
			error = df.Steer.values[3:, ] - pAngle
			out.append(error)

	if len(out) > 0:
		# concatenate out (list of np objects) into a single list
		error = numpy.concatenate(out)
		# 90th percentile of error
		alpha = numpy.nanpercentile(error, 90)

		# divide into 9 bins with edges: -5a,-2.5a,-a,a,2.5,5a
		binnedError = numpy.histogram(error, bins=[-10 * abs(alpha), -5 * abs(alpha), -2.5 * abs(alpha),
			-abs(alpha), -0.5 * abs(alpha), 0.5 * abs(alpha), abs(alpha),
			2.5 * abs(alpha), 5 * abs(alpha), 10 * abs(alpha)])

		# calculate H
		binnedArr = numpy.asarray(binnedError[0])
		binnedArr = binnedArr.astype(float)

		# check out calc of p
		p = numpy.divide(binnedArr, numpy.sum(binnedArr))
		Hp = numpy.multiply(numpy.multiply(-1, p), (numpy.log(p)/numpy.log(9)))
		Hp = Hp[~numpy.isnan(Hp)]
		Hp = numpy.sum(Hp)
	else:
		Hp = numpy.nan

	return Hp


def tailgatingTime(drivedata: pydre.core.DriveData, cutoff=2):
	tail_time = 0
	for d in drivedata.data:
		table = d
		difftime = table.SimTime.values[1:] - table.SimTime.values[:-1]
		table.loc[:, 'delta_t'] = numpy.concatenate([numpy.zeros(1), difftime])
		# find all tailgating instances where the delta time is reasonable.
		# this ensures we don't get screwy data from merged files
		tail_data = table[(table.HeadwayTime > 0) & (table.HeadwayTime < cutoff) & (abs(table.delta_t) < .5)]
		tail_time += tail_data['delta_t'][abs(table.delta_t) < .5].sum()
	return tail_time


def tailgatingPercentage(drivedata: pydre.core.DriveData, cutoff=2):
	for d in drivedata.data:
		table = d
		difftime = table.SimTime.values[1:] - table.SimTime.values[:-1]
		table.loc[:, 'delta_t'] = numpy.concatenate([numpy.zeros(1), difftime])
		# find all tailgating instances where the delta time is reasonable.
		# this ensures we don't get screwy data from merged files
		tail_data = table[(table.HeadwayTime > 0) & (table.HeadwayTime < cutoff) & (abs(table.delta_t) < .5)]
		tail_time = tail_data['delta_t'][abs(table.delta_t) < .5].sum()
		total_time = table['delta_t'][abs(table.delta_t) < .5].sum()
	return tail_time/total_time


metricsList = {}
metricsList['meanVelocity'] = meanVelocity
metricsList['steeringEntropy'] = steeringEntropy
metricsList['tailgatingTime'] = tailgatingTime
metricsList['tailgatingPercentage'] = tailgatingPercentage
