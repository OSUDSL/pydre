#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations # needed for python < 3.9

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


# metrics defined here take a list of DriveData objects and return a single floating point value

# not registered & incomplete
def findFirstTimeAboveVel(drivedata: pydre.core.DriveData, cutoff: float = 25):
    required_col = ["Velocity"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()




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

# not registered & incomplete
def findFirstTimeOutside(drivedata: pydre.core.DriveData, area: list[float]=(0, 0, 10000, 10000)):
    required_col = ["SimTime"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    timeAtEnd = 0
    for d in drivedata.data:
        if d.position >= pos:
            timeAtEnd = d.SimTime
            break
    return timeAtEnd

# helper func - check if a series only contains 0
def checkSeriesNan(series):
    count = series.value_counts()
    if (0 in count):
        if (count[0] == series.size):
            return True
    else:
        return False

def colMean(drivedata: pydre.core.DriveData, var: str, cutoff: float = 0):
    required_col = [var]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()




    total = pandas.Series(dtype='float64')
    # original code here: total = pandas.Series()
    # Got this warning on pandas 1.2.4: " DeprecationWarning: The default dtype for empty Series will be 'object' 
    # instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning."
    # Plz change it back to the original code if the current one leads to an issue
    for d in drivedata.data:
        var_dat = d[var]
        total = total.append(var_dat[var_dat >= cutoff])
    
    return numpy.mean(total.values, dtype=np.float64).astype(np.float64)


def colSD(drivedata: pydre.core.DriveData, var: str, cutoff: float = 0):
    required_col = [var]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    total = pandas.Series(dtype='float64')
    # original code here: total = pandas.Series()
    # Got this warning on pandas 1.2.4: " DeprecationWarning: The default dtype for empty Series will be 'object' 
    # instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning."
    # Plz change it back to the original code if the current one leads to an issue
    for d in drivedata.data:
        var_dat = d[var]
        total = total.append(var_dat[var_dat >= cutoff])
    return numpy.std(total.values, dtype=np.float64).astype(np.float64)


def colMax(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    maxes = []
    for d in drivedata.data:
        var_dat = d[var]
        maxes.append(var_dat.max())
    return pandas.Series(maxes).max()


def colMin(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    mins = []
    for d in drivedata.data:
        var_dat = d[var]
        mins.append(var_dat.min())
    return pandas.Series(mins).min()


def meanVelocity(drivedata: pydre.core.DriveData, cutoff: float = 0):
    required_col = ["Velocity"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    total_vel = pandas.Series(dtype='float64')
    # original code here: total_Vel = pandas.Series()
    # Got this warning on pandas 1.2.4: " DeprecationWarning: The default dtype for empty Series will be 'object' 
    # instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning."
    # Plz change it back to the original code if the current one leads to an issue
    for d in drivedata.data:
        total_vel = total_vel.append(d[d.Velocity >= cutoff].Velocity)
    return numpy.mean(total_vel.values, dtype=np.float64).astype(np.float64)


def stdDevVelocity(drivedata: pydre.core.DriveData, cutoff: float = 0):
    required_col = ["Velocity"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    total_vel = pandas.Series(dtype='float64')
    # original code here: total_Vel = pandas.Series()
    # Got this warning on pandas 1.2.4: " DeprecationWarning: The default dtype for empty Series will be 'object' 
    # instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning."
    # Plz change it back to the original code if the current one leads to an issue
    for d in drivedata.data:
        total_vel = total_vel.append(d[d.Velocity >= cutoff].Velocity)
    return numpy.std(total_vel.values, dtype=np.float64).astype(np.float64)


def timeAboveSpeed(drivedata: pydre.core.DriveData, cutoff: float = 0, percentage: bool = False):
    required_col = ["SimTime", "Velocity"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    time = 0
    total_time = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=required_col)  # drop other columns
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

# Parameters:

# Offset: the name of the specific column in the datafile, could be LaneOffset or RoadOffset

# noisy: If this is set to 'true', a low pass filter with 5 Hz cut off frequency will be applied, according to documentation
# The document doesn't specify the order of filter so I'll use 1st order here

# filfilt: if this is set to 'true', the filter will be applied twice, once forward and once backwards. This gives better results
# when testing with a sin signal, but I'm not sure if that leads to a risk or not so I'll keep that as an option

# noisy and filtfilt are NOT case sensitive and are meaningful only when calculating MSDLP
def lanePosition(drivedata: pydre.core.DriveData, laneInfo="sdlp", lane=2, lane_width=3.65, car_width=2.1, offset="LaneOffset", noisy="false", filtfilt="false"):
    required_col = ["SimTime", "DatTime", "Lane", offset]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    for d in drivedata.data:
        print("1")
        df = pandas.DataFrame(d, columns=required_col)  # drop other columns
        LPout = None
        if (df.size > 0):
            if (laneInfo in ["mean", "Mean"]):
                # mean lane position
                LPout = np.mean((df[offset]))  # abs to give mean lane "error"
            elif (laneInfo in ["msdlp", "MSDLP"]):
                samplingFrequency = 1 / np.mean(np.diff(df.DatTime)) # calculate sampling drequency based on DatTime
                # samplingFrequency = 1 / np.mean(np.diff(df.SimTime))
                
                sos = signal.butter(2, 0.1, 'high', analog=False, output='sos', fs=float(samplingFrequency)) # define butterWorthFilter
                # the output parameter can also be set to 'ba'. Under this case, signal.lfilter(b, a, array) or 
                # signal.filtfilt(b, a, array) should be used. sos is recommanded for general purpose filtering

                data = df[offset]
                if (noisy.lower() == "true"):
                    sosLow = signal.butter(1, 5, 'low', analog=False, output='sos', fs=float(samplingFrequency))
                    data = signal.sosfilt(sosLow, data)
                    # apply a low pass filter to reduce the noise

                filteredLP = None
                if (filtfilt.lower() == "true"):
                    filteredLP = signal.sosfiltfilt(sos, data) # apply the filter twice
                else:
                    filteredLP = signal.sosfilt(sos, data) # apply the filter once
                # signal.sosfiltfilt() applies the filter twice (forward & backward) while signal.sosfilt applies
                # the filter once. 
        
                LPout = np.std(filteredLP)

            elif (laneInfo in ["sdlp", "SDLP"]):
                LPout = np.std(df[offset])
                # Just cause I've been staring at this a while and want to get some code down:
                # Explanation behind this: SAE recommends using the unbiased estimator "1/n-1". The numpy code does
                # not use this, so I wrote up code that can easily be subbed in, if it's determined necessary.
                """
				entrynum = len(df[offset])
				unbiased_estimator = 1/(entrynum - 1)
				average = np.mean((df[offset]))
				variation = 0
				for entry in entrynum:
					variation += (pow(df[offset][entry] - average, 2))
				LPout = math.sqrt(unbiased_estimator * variation)
				"""
            elif (laneInfo in ["exits"]):
                LPout = (df.Lane - df.Lane.shift(1)).abs().sum()
            elif (laneInfo in ["violation_count"]):
                LPout = 0
                # tolerance is the maximum allowable offset deviation from 0
                tolerance = lane_width / 2 - car_width / 2
                is_violating = abs(df[offset]) > tolerance

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
                violations = df[abs(df[offset]) > tolerance]
                if (violations.size > 0):
                    deltas = violations.diff()
                    deltas.iloc[0] = deltas.iloc[1]
                    LPout = sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)])
            else:
                print("Not a valid lane position metric - use 'mean', 'sdlp', or 'exits'.")
                return None
    return LPout


def roadExits(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "RoadOffset", "Velocity"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    # assuming a two lane road, determine the amount of time they were not in the legal roadway
    # Lane width 3.6m, car width 1.8m
    roadOutTime = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=required_col)
        outtimes = df[(df.RoadOffset > (7.2)) | (df.RoadOffset < (0)) & (df.Velocity > 1)]
        deltas = outtimes.diff()
        if deltas.shape[0] > 0:
            deltas.iloc[0] = deltas.iloc[1]
            roadOutTime += sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)])
    return roadOutTime


def roadExitsY(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "YPos", "Velocity"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    # assuming a two lane road, determine the amount of time they were not in the legal roadway
    # Lane width 3.6m, car width 1.8m
    roadOutTime = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=required_col)
        outtimes = df[(df.YPos > (7.2 - 0.9)) | (df.YPos < (0 + 0.9))]
        deltas = outtimes.diff()
        if deltas.shape[0] > 0:
            deltas.iloc[0] = deltas.iloc[1]
            roadOutTime += sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)])
    return roadOutTime

# incomplete
def brakeJerk(drivedata: pydre.core.DriveData, cutoff: float = 0):
    required_col = ["SimTime", "LonAccel"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    a = []
    t = []
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=required_col)  # drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
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

# cutoff doesn't work
def steeringEntropy(drivedata: pydre.core.DriveData, cutoff: float = 0):
    required_col = ["SimTime", "Steer"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    out = []
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=required_col)  # drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates

        if (len(df) == 0):
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
    Hp = numpy.multiply(numpy.multiply(-1, p), (numpy.log(p) / numpy.log(9)))
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


def tailgatingPercentage(drivedata: pydre.core.DriveData, cutoff: float =2):
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


def boxMetrics(drivedata: pydre.core.DriveData, cutoff: float =0, stat: str ="count"):
    required_col = ["SimTime", "FeedbackButton", "BoxAppears"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    total_boxclicks = pandas.Series(dtype='float64')
    # original code here: total_boxclicks = pandas.Series()
    # Got this warning on pandas 1.2.4: " DeprecationWarning: The default dtype for empty Series will be 'object' 
    # instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning."
    # Plz change it back to the original code if the current one leads to an issue
    time_boxappeared = 0.0
    time_buttonclicked = 0.0
    hitButton = 0;
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=required_col)  # drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
        if (len(df) == 0):
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

            if (len(buttonClickedIndices) > 0):
                indexClicked = int(buttonClickedIndices[0])
                clickTime = simTimedf.loc[indexClicked]
                reactionTime = clickTime - startTime
                reactionTimeList.append(reactionTime)
            else:
                if (counter < len(indicesBoxOn) - 1):
                    endIndex = counter + 1;
                    endOfBox = int(indicesBoxOn[endIndex])
                    buttonClickeddf = feedbackButtondf.loc[boxOn:endOfBox - 1].diff(1)
                    buttonClickedIndices = buttonClickeddf[buttonClickeddf.values > .5].index[0:]
                    if (len(buttonClickedIndices) > 0):
                        indexClicked = int(buttonClickedIndices[0])
                        clickTime = simTimedf.loc[indexClicked]
                        reactionTime = clickTime - startTime
                        reactionTimeList.append(reactionTime)
            sum = feedbackButtondf.loc[boxOn:boxOff].sum();
            if sum > 0.000:
                hitButton = hitButton + 1
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


def firstOccurance(df: pandas.DataFrame, condition: str):
    try:
        output = df[condition].head(1)
        return output.index[0]
    except:
        return None


def numOfErrorPresses(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "TaskFail"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    presses = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=(required_col))  # drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
        p = ((df.TaskFail - df.TaskFail.shift(1)) > 0).sum()
        presses += p
    return presses


'''
TBI Reaction algorithm
To find the braking reaction time to the event (for each Section):
    Only look at values after the event E (Activation = 1)
    Find the first timestep X where:
		X is after the Event (Activation=1)
			AND
		BrakeForce(X) – BrakeForce(E) > 0
    Reaction time is Time(X) – Time(First timestep where Activation = 1)


To find the throttle reaction time to the event (for each Section):
    Only look at values after the event E (Activation = 1)
    Find the first timestep X where:
		X is after the Event (Activation=1)
			AND
		Throttle(X) – Throttle(X-1) > SD([Throttle for all X in Section where Activation !=1]).
    Reaction time is Time(X) – Time(First timestep where Activation = 1)


Then you average the two throttle reaction times and the two brake reaction times for each of the 4 DriveIDs.
This results in 8 reaction times per participant.
'''


def tbiReaction(drivedata: pydre.core.DriveData, type: str="brake", index: int =0):
    required_col = ["SimTime", "Brake", "Throttle", "MapHalf", "MapSectionLocatedIn", "HazardActivation"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=(required_col))
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
        if (len(df) == 0):
            continue

        reactionTimes = []
        simtime = df['SimTime']
        hazard = df['HazardActivation']

        hazardIndex = [1, 3][index]
        if type == "brake":
            # brakesd = numpy.std(df.Brake)
            start = firstOccurance(df, hazard == hazardIndex)
            if start:
                startTime = df["SimTime"].loc[start]
                startBrake = df["Brake"].loc[start]
                # check maximum of 10 seconds from hazard activation
                reactionTime = firstOccurance(df, (simtime > startTime)  # after the starting of the hazard
                                              & (simtime < startTime + 10)  # before 10 seconds after the hazard
                                              & (df["Brake"] > startBrake + 0.5))
                if reactionTime:
                    print(
                        "hazard {} reactiontime {}".format(hazardIndex, simtime.loc[reactionTime] - simtime.loc[start]))
                    reactionTimes.append(simtime.loc[reactionTime] - simtime.loc[start])
        elif type == "throttle":
            throttlesd = numpy.std(df[(hazard == 0) | (hazard == 2)].Throttle)
            throttlediff = df["Throttle"].diff()
            start = firstOccurance(df, hazard == hazardIndex)
            if start:
                startTime = df["SimTime"].loc[start]
                reactionTime = firstOccurance(df, (simtime > startTime)  # after the starting of the hazard
                                              & (simtime < startTime + 10)  # before 10 seconds after the hazard
                                              & (throttlediff > throttlesd))
                if reactionTime:
                    print(
                        "hazard {} reactiontime {}".format(hazardIndex, simtime.loc[reactionTime] - simtime.loc[start]))
                    reactionTimes.append(simtime.loc[reactionTime] - simtime.loc[start])

        if len(reactionTimes) > 0:
            return reactionTimes[0]
        else:
            return None


def ecoCar(drivedata: pydre.core.DriveData, FailCode: str ="1", stat: str ="mean"):
    required_col = ["SimTime", "WarningToggle", "FailureCode", "Throttle", "Brake", "Steer", "AutonomousDriving"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    event = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=(required_col))  # drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates

        if (len(df) == 0):
            continue

        warningToggledf = df['WarningToggle']
        autonomousToggledf = df['AutonomousDriving']
        throttledf = df['Throttle']
        brakedf = df['Brake']
        steerdf = df['Steer']
        simTimedf = df['SimTime']
        failureCodedf = df["FailureCode"]

        toggleOndf = warningToggledf.diff(1)
        indicesToggleOn = toggleOndf[toggleOndf.values > .5].index[0:]
        indicesToggleOff = toggleOndf[toggleOndf.values < 0.0].index[0:]

        reactionTimeList = list()

        for counter in range(0, len(indicesToggleOn)):

            warningOn = int(indicesToggleOn[counter])
            startWarning = simTimedf.loc[warningOn]
            ## End time (start of warning time plus 15 seconds)
            warningPlus15 = df[(df.SimTime >= startWarning) & (df.SimTime <= startWarning + 15)]
            indWarning = warningPlus15.index[0:]

            warningOff = int(indWarning[-1])
            endTime = simTimedf.loc[warningOff]

            if (failureCodedf.loc[warningOn] == int(FailCode)):

                rtList = list()
                ## Compare brake, throttle & steer

                # Brake Reaction
                brakeDuringWarning = brakedf.loc[warningOn:warningOff]
                reaction_Brake = 0
                initial_Brake = brakeDuringWarning.iloc[0]
                thresholdBrake = 2
                brakeVector = brakeDuringWarning[brakeDuringWarning >= (initial_Brake + thresholdBrake)]
                if (len(brakeVector > 0)):
                    brakeValue = brakeVector.iloc[0]
                    indexB = brakeVector.index[0]
                    reaction_Brake = simTimedf[indexB] - startWarning
                if (reaction_Brake > 0):
                    rtList.append(reaction_Brake)

                ## Throttle Reaction
                throttleDuringWarning = throttledf.loc[warningOn:warningOff]
                reaction_throttle = 0
                initial_throttle = throttleDuringWarning.iloc[0]
                thresholdThrottle = 2
                throttleVector = throttleDuringWarning[throttleDuringWarning >= (initial_throttle + thresholdThrottle)]
                if (len(throttleVector > 0)):
                    throttleValue = throttleVector.iloc[0]
                    indexT = throttleVector.index[0]
                    reaction_throttle = simTimedf[indexT] - startWarning
                if (reaction_throttle > 0):
                    rtList.append(reaction_throttle)

                ## Steer Reaction
                steerDuringWarning = steerdf.loc[warningOn:warningOff]
                reaction_steer = 0
                thresholdSteer = 2
                initial_steer = steerDuringWarning.iloc[0]
                steerVector = steerDuringWarning[(steerDuringWarning >= (initial_steer + thresholdSteer))]
                steerVector2 = steerDuringWarning[(steerDuringWarning <= (initial_steer - thresholdSteer))]
                steerVector.append(steerVector2)
                if (len(steerVector > 0)):
                    steerValue = steerVector.iloc[0]
                    indexS = steerVector.index[0]
                    reaction_steer = simTimedf[indexS] - startWarning

                if (reaction_steer > 0):
                    rtList.append(reaction_steer)

                # Reaction By Toggling Autonomous Back On
                autonomousDuringWarning = autonomousToggledf.loc[warningOn:warningOff]
                reaction_autonomous = 0
                autonomousOndf = autonomousDuringWarning.diff(1)
                autonomousToggleOn = autonomousOndf[autonomousOndf.values > .5].index[0:]
                if (len(autonomousToggleOn) > 0):
                    indexA = int(autonomousToggleOn[0])
                    reaction_autonomous = simTimedf[indexA] - startWarning

                if (reaction_autonomous > 0):
                    rtList.append(reaction_autonomous)

                # Compare all Reaction Times
                if (len(rtList) != 0):
                    reactionTime = min(rtList)
                    reactionTimeList.append(reactionTime)

        reactionTimeList = [x for x in reactionTimeList if x != None]

        if stat == "mean":
            mean = None
            if (len(reactionTimeList) > 0):
                mean = numpy.mean(reactionTimeList, axis=0)
            return mean
        elif stat == "sd":
            sd = None
            if (len(reactionTimeList) > 0):
                sd = numpy.std(reactionTimeList, axis=0)
            return sd
        elif stat == "event":
            return len(reactionTimeList)
        else:
            print("Can't calculate that statistic.")


def appendDFToCSV_void(df, csvFilePath: str, sep: str =","):
    import os
    if not os.path.isfile(csvFilePath):
        df.to_csv(csvFilePath, mode='a', index=False, sep=sep)
    elif len(df.columns) != len(pandas.read_csv(csvFilePath, nrows=1, sep=sep).columns):
        raise Exception(
            "Columns do not match!! Dataframe has " + str(len(df.columns)) + " columns. CSV file has " + str(
                len(pandas.read_csv(csvFilePath, nrows=1, sep=sep).columns)) + " columns.")
    elif not (df.columns == pandas.read_csv(csvFilePath, nrows=1, sep=sep).columns).all():
        raise Exception("Columns and column order of dataframe and csv file do not match!!")
    else:
        df.to_csv(csvFilePath, mode='a', index=False, sep=sep, header=False)


def gazeNHTSA(drivedata: pydre.core.DriveData):
    required_col = ["VidTime", "gaze", "gazenum", "TaskFail", "taskblocks", "PartID"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    numofglances = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=(required_col))  # drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates

        if (len(df) == 0):
            continue

        # construct table with columns [glanceduration, glancelocation, error]
        gr = df.groupby('gazenum', sort=False)
        durations = gr['VidTime'].max() - gr['VidTime'].min()
        locations = gr['gaze'].first()
        error_list = gr['TaskFail'].any()

        glancelist = pandas.DataFrame({'duration': durations, 'locations': locations, 'errors': error_list})
        glancelist['locations'].fillna('offroad', inplace=True)
        glancelist['locations'].replace(['car.WindScreen', 'car.dashPlane', 'None'], ['onroad', 'offroad', 'offroad'],
                                        inplace=True)

        # print(d.columns.values)
        # print("Task {}, Trial {}".format(d["TaskID"].min(), d["taskblocks"].min()))
        # print(glancelist)

        glancelist_aug = glancelist
        glancelist_aug['TaskID'] = d["TaskID"].min()
        glancelist_aug['taskblock'] = d["taskblocks"].min()
        glancelist_aug['Subject'] = d["PartID"].min()

        appendDFToCSV_void(glancelist_aug, "glance_list.csv")

        # table constructed, now find metrics
        # glancelist['over2s'] = glancelist['duration'] > 2

        num_over_2s_offroad_glances = glancelist[(glancelist['duration'] > 2) &
                                                 (glancelist['locations'] == 'offroad')]['duration'].count()

        num_offroad_glances = glancelist[(glancelist['locations'] == 'offroad')]['duration'].count()

        total_time_offroad_glances = glancelist[(glancelist['locations'] == 'offroad')]['duration'].sum()

        mean_time_offroad_glances = glancelist[(glancelist['locations'] == 'offroad')]['duration'].mean()

        # print(">2s glances: {}, num glances: {}, total time glances: {}, mean time glances {}".format(
        #	num_over_2s_offroad_glances, num_offroad_glances, total_time_offroad_glances, mean_time_offroad_glances))

        return [num_offroad_glances, num_over_2s_offroad_glances, mean_time_offroad_glances, total_time_offroad_glances]
    return [None, None, None, None]


metricsList = {}
metricsColNames = {}


def registerMetric(name, function, columnnames: str =None):
    metricsList[name] = function
    if columnnames:
        metricsColNames[name] = columnnames
    else:
        metricsColNames[name] = [name, ]


#not working
def addVelocities(drivedata: pydre.core.DriveData):
    df = pandas.DataFrame;
    for d in drivedata.data:
        df = pandas.DataFrame(d)
    # add column with ownship velocity
        g = np.gradient(df.XPos.values, df.SimTime.values)
        df.insert(len(df.columns), "OwnshipVelocity", g, True)
    # add column with leadcar velocity
        headwayDist = df.HeadwayTime*df.OwnshipVelocity
        # v = df.OwnshipVelocity+np.gradient(headwayDist, df.SimTime.values)
        df.insert(len(df.columns), "LeadCarPos", headwayDist+df.XPos.values, True)
        df.insert(len(df.columns), "HeadwayDist", headwayDist, True)
        v = np.gradient(headwayDist + df.XPos.values, df.SimTime.values)
        df.insert(len(df.columns), "LeadCarVelocity", v, True)
    return df


def crossCorrelate(drivedata: pydre.core.DriveData):

    for d in drivedata.data:
        df = pandas.DataFrame(d)
        if 'OwnshipVelocity' not in df.columns or 'LeadCarVelocity' not in df.columns:
            df = addVelocities(drivedata)
            print("calling addVelocities()")

        v2 = df.LeadCarVelocity
        v1 = df.OwnshipVelocity
        cor = signal.correlate(v1-v1.mean(),
                                       v2-v2.mean(), mode='same')
        # cor-An N-dimensional array containing a subset of the discrete linear cross-correlation of in1 with in2.
        # delay index at the max
        df.insert(len(df.columns), "CrossCorrelations", cor, True)
        delayIndex = np.argmax(cor)
        if(delayIndex > 0):
            v2 = df.LeadCarVelocity.iloc[delayIndex:df.columns.__len__()]
            v1 = df.OwnshipVelocity.iloc[delayIndex:df.columns.__len__()]
        #normalize vectors
        v1_norm = v1/np.linalg.norm(v1)
        v2_norm = v2/np.linalg.norm(v2)
        cor = np.dot(v1_norm, v2_norm)
        if(cor > 0):
            return cor
        else:
            return 0.0

def speedbumpHondaGaze(drivedata: pydre.core.DriveData):
    required_col = ["DatTime", "gaze", "gazenum", "TaskNum", "taskblocks", "PartID"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()


            
    numofglances = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d, columns=required_col)  # drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
        
        if (len(df) == 0):
            continue
        
        # construct table with columns [glanceduration, glancelocation, error]
        gr = df.groupby('gazenum', sort=False)
        durations = gr['DatTime'].max() - gr['DatTime'].min()
        locations = gr['gaze'].first()
        error_list = gr['TaskNum'].any()
        
        glancelist = pandas.DataFrame({'duration': durations, 'locations': locations, 'errors': error_list})
        glancelist['locations'].fillna('offroad', inplace=True)
        glancelist['locations'].replace(['car.WindScreen', 'car.dashPlane', 'None'], ['onroad', 'offroad', 'offroad'],
                                        inplace=True)
        

        glancelist_aug = glancelist
        glancelist_aug['TaskNum'] = d["TaskNum"].min()
        glancelist_aug['taskblock'] = d["taskblocks"].min()
        glancelist_aug['Subject'] = d["PartID"].min()

        appendDFToCSV_void(glancelist_aug, "glance_list.csv")

        # table constructed, now find metrics


        num_onroad_glances = glancelist[(glancelist['locations'] == 'onroad')]['duration'].count()


        total_time_onroad_glances = glancelist[(glancelist['locations'] == 'onroad')]['duration'].sum()
        percent_onroad = total_time_onroad_glances / (df['DatTime'].max() - df['DatTime'].min())

        mean_time_offroad_glances = glancelist[(glancelist['locations'] == 'offroad')]['duration'].mean()
        mean_time_onroad_glances = glancelist[(glancelist['locations'] == 'onroad')]['duration'].mean()


        return [total_time_onroad_glances, percent_onroad, mean_time_offroad_glances, mean_time_onroad_glances]
    return [None, None, None, None]

def speedbumpHondaGaze2(drivedata: pydre.core.DriveData, timecolumn="DatTime", maxtasknum=5):
    required_col = [timecolumn, "gaze", "gazenum", "TaskNum", "TaskFail", "TaskInstance"] 
    # filters.numberTaskInstances() is required. 
    #for now I just assume the input dataframe has a TaskInstance column
    #diff = drivedata.checkColumns(required_col)
    
    #if (len(diff) > 0):
    #    logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
    #    raise pydre.core.ColumnsMatchError()

    for d in drivedata.data:
        logger.warning("Processing Task {}".format(d.TaskNum.mean()))
        if d.TaskNum.mean() == 0 or d.TaskNum.mean() > maxtasknum:
            return [None, None, None, None]
        df = pandas.DataFrame(d, columns=required_col)  # drop other columns
        df = df.dropna(axis=0, how='any')  # remove nans and drop duplicates
        
        df['time_diff'] = df[timecolumn].diff() # get durations by calling time_column.diff()

        df = df[df.gaze != 'onroad']   # remove onroad rows
        df.to_csv('AAM_cp1.csv')
        df = df.loc[(df['TaskInstance'] != 0) & (df['TaskInstance'] != np.nan)] # drop all rows that are not in any task instance
        dropped_instances = df.loc[(df['TaskFail'] == 1)]
        dropped_instances = dropped_instances['TaskInstance'].drop_duplicates() # get all the task instances that contains a fail and needs to be dropped
        df = df.loc[~df['TaskInstance'].isin(dropped_instances)] # drop all the failed task instances
        df.to_csv('AAM_cp2.csv')
        
        # get first 8 task instances
        number_valid_instance = df['TaskInstance'].unique()
        if len(number_valid_instance) > 8:
            lowest_instance_no = number_valid_instance.min()
            len_of_drop = len(dropped_instances.loc[dropped_instances < (lowest_instance_no + 8)])
            highest_instance_no = lowest_instance_no + 8 + len_of_drop
            df = df.loc[(df['TaskInstance'] < highest_instance_no) & (df['TaskInstance'] >= lowest_instance_no)]
            #logger.warning(highest_instance_no)
            #logger.warning(lowest_instance_no)
        elif len(number_valid_instance) < 8:
            logger.warning("Not enough valid task instances. Found {}".format(len(number_valid_instance)))

        #df = df[df.TaskInstance < 9] # only keep the glance data for the first eight task instances for each task per person. 
        
        #print(df)
        #df.to_csv('df.csv')

        group_by_gazenum = df.groupby('gazenum', sort=False) 
        durations_by_gazenum = group_by_gazenum.sum()
        durations_by_gazenum = durations_by_gazenum.loc[(durations_by_gazenum['time_diff']!=0.0)]
        #print(durations_by_gazenum)
        percentile = np.percentile(durations_by_gazenum.time_diff, 85) # find the 85th percentile value (A1)

        group_by_instance = df.groupby('TaskInstance', sort=False) # A2
        durations_by_instance = group_by_instance.sum()
        #print(durations_by_instance)
        sum_mean = durations_by_instance.time_diff.mean() # mean of duration sum
        sum_median = durations_by_instance.time_diff.median() # median of duration sum
        sum_std = durations_by_instance.time_diff.std() # std of duration sum

        return [percentile, sum_mean, sum_median, sum_std]

    return [None, None, None, None]

def getTaskNum(drivedata: pydre.core.DriveData):
    required_col = ["TaskNum"]
    diff = drivedata.checkColumns(required_col)
    
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()



    taskNum = 0
    for d in drivedata.data:
        df = pandas.DataFrame(d)
        taskNum = df['TaskNum'].mode()
        if(len(taskNum)>0):
            return taskNum[0]
        else:
            return None  






registerMetric('colMean', colMean)
registerMetric('colMin', colMin)
registerMetric('colMax', colMax)
registerMetric('colSD', colSD)
registerMetric('meanVelocity', meanVelocity)
registerMetric('stdDevVelocity', stdDevVelocity)
registerMetric('steeringEntropy', steeringEntropy)
registerMetric('tailgatingTime', tailgatingTime)
registerMetric('tailgatingPercentage', tailgatingPercentage)
registerMetric('timeAboveSpeed', timeAboveSpeed)
registerMetric('lanePosition', lanePosition)
registerMetric('boxMetrics', boxMetrics)
registerMetric('roadExits', roadExits)
registerMetric('brakeJerk', brakeJerk)
registerMetric('ecoCar', ecoCar)
registerMetric('tbiReaction', tbiReaction)
registerMetric('errorPresses', numOfErrorPresses)
registerMetric('crossCorrelate', crossCorrelate)
registerMetric('speedbumpHondaGaze', speedbumpHondaGaze, ['total_time_onroad_glance', 'percent_onroad', 'avg_offroad', 'avg_onroad'])
registerMetric('gazes', gazeNHTSA,
               ['numOfGlancesOR', 'numOfGlancesOR2s', 'meanGlanceORDuration', 'sumGlanceORDuration'])
registerMetric('speedbumpHondaGaze2', speedbumpHondaGaze2,
               ['85th_percentile', 'duration_mean', 'duration_median', 'duration_std'])
registerMetric('getTaskNum', getTaskNum)
