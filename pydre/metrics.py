#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas
import pydre.core
import numpy
import numpy as np
import math
import logging
logger = logging.getLogger(__name__)


import pdb


# metrics defined here take a list of DriveData objects and return a single floating point value
def meanVelocity(drivedata: pydre.core.DriveData, cutoff=0):
	total_vel = pandas.Series()
	for d in drivedata.data:
		total_vel = total_vel.append(d[d.Velocity >= cutoff].Velocity)
	return numpy.mean(total_vel.values, dtype=np.float64).astype(np.float64)


def timeAboveSpeed(drivedata: pydre.core.DriveData, cutoff=20, percentage=False):
	time = 0
	total_time = 0
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "Velocity"))  # drop other columns
		df['Duration'] = pandas.Series(np.gradient(df.SimTime.values), index=df.index)
		# merged files might have bad splices.  This next line avoids time-travelling.
		df.Duration[df.Duration < 0] = np.median(df.Duration.values)
		time += np.sum(df[df.Velocity > cutoff].Duration.values)
		total_time += max(df.SimTime)-min(df.SimTime)
	if percentage:
		out = time / total_time
	else:
		out = time
	return out

def lanePosition(drivedata: pydre.core.DriveData,laneInfo = "sdlp",lane=2, lane_width = 3.65, car_width = 2.1):
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "Lane", "LaneOffset"))  #drop other columns
		LPout = None
		if (df.size > 0):
			if(laneInfo in ["mean","Mean"]):
				#mean lane position
				LPout = np.mean((df.LaneOffset)) #abs to give mean lane "error"
			elif(laneInfo in ["sdlp", "SDLP"]):
				LPout = np.std(df.LaneOffset)
			elif(laneInfo in ["exits"]):
				LPout = 0
				laneno = df.Lane.values		
				for i in laneno[1:]: #ignore first item 
					if laneno[i] != laneno[i-1]:
						LPout = LPout + 1
			elif(laneInfo in ["violation_count"]):
				LPout = 0
				#tolerance is the maximum allowable offset deviation from 0
				tolerance = lane_width/2 - car_width/2
				is_violating = abs(df.LaneOffset) > tolerance
				
				#Shift the is_violating array and look for differences. Count
				#a lane violation if we start in the wrong lane.
				shifted = is_violating.shift(1)
				shifted.iloc[0] = is_violating.iloc[0]
				if (is_violating.iloc[0] == True):
					LPout = LPout + 1
				
				compare = shifted != is_violating
				
				LPout = LPout + compare.loc[compare == True].size
			elif(laneInfo in ["violation_duration"]):
				LPout = 0
				tolerance = lane_width/2 - car_width/2
				violations = df[abs(df.LaneOffset) > tolerance]
				if (violations.size > 0):
					deltas = violations.diff()
					deltas.iloc[0] = deltas.iloc[1]
					LPout = sum(deltas.SimTime[deltas.SimTime < .5])
			else:
				print("Not a valid lane position metric - use 'mean', 'sdlp', or 'exits'.")
				return None
	return LPout
	
def brakeJerk(drivedata: pydre.core.DriveData, cutoff=0):
	a = []
	t = []
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "LonAccel"))  # drop other columns
		df = pandas.DataFrame.drop_duplicates(df.dropna(axis=[0, 1], how='any'))  # remove nans and drop duplicates
		a.append = df.LonAccel
		t.append = df.simTime
	jerk = np.gradient(a, np.gradient(t))
	count = 0
	flag = 0
	for i in jerk:
		if jerk(i) >= cutoff and flag == 0:
			count = count + 1
			flag = 1
		elif jerk(i) < cutoff:
			flag = 0
	return count


def steeringEntropy(drivedata: pydre.core.DriveData, cutoff=0):
	out = []
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "Steer"))  # drop other columns
		df = pandas.DataFrame.drop_duplicates(df.dropna(axis=[0, 1], how='any'))  # remove nans and drop duplicates

		if(len(df) == 0):

			continue
			
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

	# concatenate out (list of np objects) into a single list
	if(len(out) ==0):
		return 0
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
	total_time = 0
	tail_time = 0
	for d in drivedata.data:
		table = d
		difftime = table.SimTime.values[1:] - table.SimTime.values[:-1]
		table.loc[:, 'delta_t'] = numpy.concatenate([numpy.zeros(1), difftime])
		# find all tailgating instances where the delta time is reasonable.
		# this ensures we don't get screwy data from merged files
		tail_data = table[(table.HeadwayTime > 0) & (table.HeadwayTime < cutoff) & (abs(table.delta_t) < .5)]
		tail_time += tail_data['delta_t'][abs(table.delta_t) < .5].sum()
		total_time += table['delta_t'][abs(table.delta_t) < .5].sum()
	return tail_time/total_time


metricsList = {}
metricsList['meanVelocity'] = meanVelocity
metricsList['steeringEntropy'] = steeringEntropy
metricsList['tailgatingTime'] = tailgatingTime
metricsList['tailgatingPercentage'] = tailgatingPercentage
metricsList['timeAboveSpeed'] = timeAboveSpeed
metricsList['lanePosition'] = lanePosition