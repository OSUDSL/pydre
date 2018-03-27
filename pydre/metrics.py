#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas
import pydre.core
import numpy
import numpy as np
import math
import logging
import ctypes
logger = logging.getLogger('PydreLogger')

# metrics defined here take a list of DriveData objects and return a single floating point value
def findFirstTimeAboveVel(drivedata: pydre.core.DriveData, cutoff = 25):
	timestepID = -1
	breakOut = False
	for d in drivedata.data:
		for i, row in d.iterrows():
			if row.Velocity >= cutoff:
				timestepID = i
				breakOut = True
				break
		if breakOut:
			break
	return timestepID
	
def findFirstTimeOutside(drivedata: pydre.core.DriveData, area=(0,0,10000,10000)):
	timeAtEnd = 0
	for d in drivedata.data:
		if d.position >= pos:
			timeAtEnd = d.simTime
			break
	return timeAtEnd

def colMean(drivedata: pydre.core.DriveData, var, cutoff=0):
	total = pandas.Series()
	for d in drivedata.data:
		var_dat = d[var]
		total = total.append(var_dat[var_dat >= cutoff])
	return numpy.mean(total.values, dtype=np.float64).astype(np.float64)

def colSD(drivedata: pydre.core.DriveData, var, cutoff=0):
	total = pandas.Series()
	for d in drivedata.data:
		var_dat = d[var]
		total = total.append(var_dat[var_dat >= cutoff])
	return numpy.std(total.values, dtype=np.float64).astype(np.float64)


def meanVelocity(drivedata: pydre.core.DriveData, cutoff=0):
	total_vel = pandas.Series()
	for d in drivedata.data:
		total_vel = total_vel.append(d[d.Velocity >= cutoff].Velocity)
	return numpy.mean(total_vel.values, dtype=np.float64).astype(np.float64)


def stdDevVelocity(drivedata: pydre.core.DriveData, cutoff=0):
	total_vel = pandas.Series()
	for d in drivedata.data:
		total_vel = total_vel.append(d[d.Velocity >= cutoff].Velocity)
	return numpy.std(total_vel.values, dtype=np.float64).astype(np.float64)


def timeAboveSpeed(drivedata: pydre.core.DriveData, cutoff=20, percentage=False):
	time = 0
	total_time = 0
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "Velocity"))  # drop other columns
		if df.shape[0] < 2:
			continue
		df['Duration'] = pandas.Series(np.gradient(df.SimTime.values), index=df.index)
		# merged files might have bad splices.  This next line avoids time-travelling.
		df.Duration[df.Duration < 0] = np.median(df.Duration.values)
		time += np.sum(df[df.Velocity > cutoff].Duration.values)
		total_time += max(df.SimTime) - min(df.SimTime)
	if percentage:
		out = time / total_time
	else:
		out = time
	return out

def lanePosition(drivedata: pydre.core.DriveData,laneInfo = "sdlp",lane=2, lane_width = 3.65, car_width = 2.1):
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "Lane", "LaneOffset"))  # drop other columns
		LPout = None
		if (df.size > 0):
			if(laneInfo in ["mean", "Mean"]):
				# mean lane position
				LPout = np.mean((df.LaneOffset))  # abs to give mean lane "error"
			elif(laneInfo in ["sdlp", "SDLP"]):
				LPout = np.std(df.LaneOffset)
			elif(laneInfo in ["exits"]):
				LPout = 0
				laneno = df.Lane.values
				for i in laneno[1:]:  # ignore first item
					if laneno[i] != laneno[i - 1]:
						LPout = LPout + 1
			elif(laneInfo in ["violation_count"]):
				LPout = 0
				# tolerance is the maximum allowable offset deviation from 0
				tolerance = lane_width / 2 - car_width / 2
				is_violating = abs(df.LaneOffset) > tolerance

				# Shift the is_violating array and look for differences.
				shifted = is_violating.shift(1)
				shifted.iloc[0] = is_violating.iloc[0]

				# Create an array which is true whenever the car goes in/out of
				# the lane
				compare = shifted != is_violating

				# shiftout becomes an array which only has elements each time
				# compare is true (ie, violation status changed). These elements
				# are True when the direction is out of the lane, False when the
				# direction is back into the lane. We only count the out shifts.
				shifts = compare.loc[compare == True] == is_violating.loc[compare == True]
				shiftout = shifts.loc[shifts == True]

				# Count all violations. Add one if the region begins with a violation.
				if is_violating.iloc[0] is True:
					LPout = LPout + 1
				LPout = LPout + shiftout.size

			elif laneInfo in ["violation_duration"]:
				LPout = 0
				tolerance = lane_width / 2 - car_width / 2
				violations = df[abs(df.LaneOffset) > tolerance]
				if (violations.size > 0):
					deltas = violations.diff()
					deltas.iloc[0] = deltas.iloc[1]
					LPout = sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)  ])
			else:
				print("Not a valid lane position metric - use 'mean', 'sdlp', or 'exits'.")
				return None
	return LPout

def roadExits(drivedata: pydre.core.DriveData): 
	# assuming a two lane road, determine the amount of time they were not in the legal roadway
	# Lane width 3.6m, car width 1.8m
	roadOutTime = 0
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "RoadOffset", "Velocity"))
		outtimes = df[(df.RoadOffset > (7.2)) | (df.RoadOffset < (0)) & (df.Velocity > 1)]
		deltas = outtimes.diff()
		if deltas.shape[0] > 0:
			deltas.iloc[0] = deltas.iloc[1]
			roadOutTime += sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)  ])
	return roadOutTime

def roadExitsY(drivedata: pydre.core.DriveData): 
	# assuming a two lane road, determine the amount of time they were not in the legal roadway
	# Lane width 3.6m, car width 1.8m
	roadOutTime = 0
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "YPos", "Velocity"))
		outtimes = df[(df.YPos > (7.2-0.9)) | (df.YPos < (0+0.9))]
		deltas = outtimes.diff()
		if deltas.shape[0] > 0:
			deltas.iloc[0] = deltas.iloc[1]
			roadOutTime += sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)  ])
	return roadOutTime

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
	if len(out) == 0:
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
	return tail_time / total_time
	
def boxMetrics(drivedata: pydre.core.DriveData, cutoff=0, stat="count"):
	total_boxclicks = pandas.Series()
	time_boxappeared = 0.0
	time_buttonclicked = 0.0
	hitButton = 0;
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "FeedbackButton", "BoxAppears"))  # drop other columns
		df = pandas.DataFrame.drop_duplicates(df.dropna(axis=[0, 1], how='any'))  # remove nans and drop duplicates
		if(len(df) == 0):
			continue
		boxAppearsdf = df['BoxAppears']
		simTimedf = df['SimTime']
		boxOndf = boxAppearsdf.diff(1)
		indicesBoxOn = boxOndf[boxOndf.values > .5].index[0:]
		indicesBoxOff = boxOndf[boxOndf.values < 0.0].index[0:]
		feedbackButtondf = df['FeedbackButton']
		reactionTimeList = list();
		for counter in range(0, len(indicesBoxOn)):
			boxOn = int(indicesBoxOn[counter])
			boxOff = int(indicesBoxOff[counter])
			startTime = simTimedf.loc[boxOn]
			buttonClickeddf = feedbackButtondf.loc[boxOn:boxOff].diff(1)
			buttonClickedIndices = buttonClickeddf[buttonClickeddf.values > .5].index[0:]
			
			if(len(buttonClickedIndices) > 0):
				indexClicked = int(buttonClickedIndices[0])
				clickTime = simTimedf.loc[indexClicked]
				reactionTime = clickTime - startTime
				reactionTimeList.append(reactionTime)
			else:
				if(counter < len(indicesBoxOn) - 1):
					endIndex = counter + 1;
					endOfBox = int(indicesBoxOn[endIndex])
					buttonClickeddf = feedbackButtondf.loc[boxOn:endOfBox - 1].diff(1)
					buttonClickedIndices = buttonClickeddf[buttonClickeddf.values > .5].index[0:]
					if(len(buttonClickedIndices) > 0):
						indexClicked = int(buttonClickedIndices[0])
						clickTime = simTimedf.loc[indexClicked]
						reactionTime = clickTime - startTime
						reactionTimeList.append(reactionTime)
			sum = feedbackButtondf.loc[boxOn:boxOff].sum();
			if sum > 0.000:
				hitButton = hitButton + 1;
		if stat == "count":
			return hitButton
		elif stat == "mean":
			mean = numpy.mean(reactionTimeList, axis=0)
			return mean
		elif stat == "sd":
			sd = numpy.std(reactionTimeList, axis=0)
			return sd
		else:
			print("Can't calculate that statistic.")
	return hitButton

def ecoCar(drivedata: pydre.core.DriveData, FailCode= "1", stat= "mean"):
	event=0
	for d in drivedata.data:
		df = pandas.DataFrame(d, columns=("SimTime", "WarningToggle","FailureCode", "Throttle", "Brake", "Steer","AutonomousDriving"))  # drop other columns
		df = pandas.DataFrame.drop_duplicates(df.dropna(axis=[0, 1], how='any'))  # remove nans and drop duplicates
			
		if(len(df) == 0):
			continue
			
		warningToggledf = df['WarningToggle']
		autonomousToggledf = df['AutonomousDriving']
		throttledf = df['Throttle']
		brakedf = df['Brake']
		steerdf= df['Steer']
		simTimedf = df['SimTime']
		failureCodedf= df["FailureCode"]
		
		
		toggleOndf= warningToggledf.diff(1)		
		indicesToggleOn = toggleOndf[toggleOndf.values > .5].index[0:] 
		indicesToggleOff = toggleOndf[toggleOndf.values < 0.0].index[0:]
		
	
		reactionTimeList = list();

		
		for counter in range(0, len(indicesToggleOn)):
			
			warningOn = int(indicesToggleOn[counter])		
			startWarning = simTimedf.loc[warningOn]
			## End time (start of warning time plus 15 seconds)	
			warningPlus15 = df[(df.SimTime >= startWarning) & (df.SimTime <= startWarning+15)]
			indWarning = warningPlus15.index[0:]
			
			warningOff = int (indWarning[-1])
			endTime= simTimedf.loc[warningOff]
				
			if(failureCodedf.loc[warningOn]== int(FailCode)):
				
				if (stat == "event"):
					event+=1
				else: 
					rtList=list()
					## Compare brake, throttle & steer 
					
					#Brake Reaction 
					brakeDuringWarning = brakedf.loc[warningOn:warningOff]
					reaction_Brake= 0	
					initial_Brake = brakeDuringWarning.iloc[0]
					thresholdBrake=2
					brakeVector = brakeDuringWarning[brakeDuringWarning>=(initial_Brake+thresholdBrake)]
					if(len(brakeVector>0)):
						brakeValue=brakeVector.iloc[0]
						indexB = brakeVector.index[0]
						reaction_Brake = simTimedf[indexB]-startWarning
					if (reaction_Brake != 0):
						rtList.append(reaction_Brake)
						
						
					## Throttle Reaction
					throttleDuringWarning= throttledf.loc[warningOn:warningOff]
					reaction_throttle = 0
					initial_throttle = throttleDuringWarning.iloc[0]
					thresholdThrottle=2	
					throttleVector = throttleDuringWarning[throttleDuringWarning>=(initial_throttle+thresholdThrottle)]					
					if(len(throttleVector>0)):
						throttleValue=throttleVector.iloc[0]
						indexT = throttleVector.index[0]
						reaction_throttle = simTimedf[indexT]-startWarning
					if (reaction_throttle != 0):
						rtList.append(reaction_throttle)
					
					## Steer Reaction
					steerDuringWarning= steerdf.loc[warningOn:warningOff]
					reaction_steer = 0
					thresholdSteer=2
					initial_steer = steerDuringWarning.iloc[0]					
					steerVector =steerDuringWarning[(steerDuringWarning >= (initial_steer+thresholdSteer))]
					steerVector2= steerDuringWarning[(steerDuringWarning <= (initial_steer-thresholdSteer))]
					steerVector.append(steerVector2)
					if(len(steerVector>0)):
						steerValue=steerVector.iloc[0]
						indexS = steerVector.index[0]
						reaction_steer = simTimedf[indexS]-startWarning
						
					if (reaction_steer != 0):
						rtList.append(reaction_steer)
				
					#Reaction By Toggling Autonomous Back On
					autonomousDuringWarning = autonomousToggledf.loc[warningOn:warningOff]
					reaction_autonomous = 0	
					autonomousOndf= autonomousDuringWarning.diff(1)		
					autonomousToggleOn = autonomousOndf[autonomousOndf.values > .5].index[0:] 
					if(len(autonomousToggleOn)>0):
						indexA = int (autonomousToggleOn[0])
						reaction_autonomous = simTimedf[indexA] - startWarning
					
					if (reaction_autonomous != 0):
						rtList.append(reaction_autonomous)
					
					#Compare all Reaction Times	
					if(len(rtList) != 0):					
						reactionTime = min(rtList)	
					else: 
						reactionTime = -1
						
					reactionTimeList.append(reactionTime)
		
		if stat == "mean":
			mean = -1
			if (len(reactionTimeList) > 0):
				mean = numpy.mean(reactionTimeList, axis=0)
			return mean
		elif stat == "sd":
			sd = -1
			if (len(reactionTimeList) > 0):
				sd = numpy.std(reactionTimeList, axis=0)
			return sd
		elif stat == "event":
			return event	
		else:
			print("Can't calculate that statistic.")
	
metricsList = {}
metricsList['colMean'] = colMean
metricsList['colSD'] = colSD
metricsList['meanVelocity'] = meanVelocity
metricsList['stdDevVelocity'] = stdDevVelocity
metricsList['steeringEntropy'] = steeringEntropy
metricsList['tailgatingTime'] = tailgatingTime
metricsList['tailgatingPercentage'] = tailgatingPercentage
metricsList['timeAboveSpeed'] = timeAboveSpeed
metricsList['lanePosition'] = lanePosition
metricsList['boxMetrics'] = boxMetrics
metricsList['roadExits'] = roadExits
metricsList['brakeJerk'] = brakeJerk
metricsList['ecoCar'] = ecoCar
