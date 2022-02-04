from __future__ import annotations  # needed for python < 3.9

import logging
import pandas
import pydre.core
from pydre.metrics import registerMetric
import numpy as np
import math
from scipy import signal

# metrics defined here take a list of DriveData objects and return a single floating point value

# not registered & incomplete
from pydre.metrics.driverdistraction import getTaskNum, numOfErrorPresses, gazeNHTSA, crossCorrelate, \
    speedbumpHondaGaze, speedbumpHondaGaze2, eventCount, insDuration, speedbump2Gaze

logger = logging.getLogger(__name__)


@registerMetric()
def findFirstTimeAboveVel(drivedata: pydre.core.DriveData, cutoff: float = 25):
    required_col = ["Velocity"]
    drivedata.checkColumns(required_col)
    timestepID = -1
    # TODO: reimplement with selection and .head(1)

    for i, row in drivedata.data.iterrows():
        if row.Velocity >= cutoff:
            timestepID = i
            break

    return timestepID


# def findFirstTimeOutside(drivedata: pydre.core.DriveData, area: list[float] = (0, 0, 10000, 10000)):
# TODO: implement with selection and .head(1)


# helper func - check if a series only contains 0
def checkSeriesNan(series):
    count = series.value_counts()
    if (0 in count):
        if (count[0] == series.size):
            return True
    else:
        return False

@registerMetric()
def colMean(drivedata: pydre.core.DriveData, var: str, cutoff: float = 0):
    required_col = [var]
    drivedata.checkColumns(required_col)
    var_dat = drivedata.data[var]
    return np.mean(var_dat[var_dat >= cutoff].values)

@registerMetric()
def colSD(drivedata: pydre.core.DriveData, var: str, cutoff: float = 0):
    required_col = [var]
    drivedata.checkColumns(required_col)
    var_dat = drivedata.data[var]
    return np.std(var_dat[var_dat >= cutoff].values)

@registerMetric()
def colMax(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    drivedata.checkColumns(required_col)
    var_dat = drivedata.data[var]
    return np.max(var_dat.values)

@registerMetric()
def colMin(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    drivedata.checkColumns(required_col)
    var_dat = drivedata.data[var]
    return np.min(var_dat.values)

@registerMetric()
def timeAboveSpeed(drivedata: pydre.core.DriveData, cutoff: float = 0, percentage: bool = False):
    required_col = ["SimTime", "Velocity"]
    drivedata.checkColumns(required_col)

    df = pandas.DataFrame(drivedata.data, columns=required_col)  # drop other columns
    if df.shape[0] < 2:
        return None
    df['Duration'] = pandas.Series(np.gradient(df.SimTime.values), index=df.index)
    # merged files might have bad splices.  This next line avoids time-travelling.
    df.Duration[df.Duration < 0] = 0
    time = np.sum(df[df.Velocity > cutoff].Duration.values)
    total_time = max(df.SimTime) - min(df.SimTime)
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
@registerMetric()
def lanePosition(drivedata: pydre.core.DriveData, laneInfo="sdlp", lane=2, lane_width=3.65, car_width=2.1,
                 offset="LaneOffset", noisy="false", filtfilt="false"):
    required_col = ["SimTime", "DatTime", "Lane", offset]
    drivedata.checkColumns(required_col)

    df = pandas.DataFrame(drivedata.data, columns=required_col)  # drop other columns
    LPout = None
    if (df.size > 0):
        if (laneInfo in ["mean", "Mean"]):
            # mean lane position
            LPout = np.mean((df[offset]))  # abs to give mean lane "error"
        elif (laneInfo in ["msdlp", "MSDLP"]):
            samplingFrequency = 1 / np.mean(np.diff(df.DatTime))  # calculate sampling drequency based on DatTime
            # samplingFrequency = 1 / np.mean(np.diff(df.SimTime))

            sos = signal.butter(2, 0.1, 'high', analog=False, output='sos',
                                fs=float(samplingFrequency))  # define butterWorthFilter
            # the output parameter can also be set to 'ba'. Under this case, signal.lfilter(b, a, array) or
            # signal.filtfilt(b, a, array) should be used. sos is recommanded for general purpose filtering

            data = df[offset]
            if (noisy.lower() == "true"):
                sosLow = signal.butter(1, 5, 'low', analog=False, output='sos', fs=float(samplingFrequency))
                data = signal.sosfilt(sosLow, data)
                # apply a low pass filter to reduce the noise

            filteredLP = None
            if (filtfilt.lower() == "true"):
                filteredLP = signal.sosfiltfilt(sos, data)  # apply the filter twice
            else:
                filteredLP = signal.sosfilt(sos, data)  # apply the filter once
            # signal.sosfiltfilt() applies the filter twice (forward & backward) while signal.sosfilt applies
            # the filter once.

            LPout = np.std(filteredLP)

        elif (laneInfo in ["sdlp", "SDLP"]):
            LPout = np.std(df[offset])
            # Just cause I've been staring at this a while and want to get some code down:
            # Explanation behind this: SAE recommends using the unbiased estimator "1/n-1". The np code does
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

@registerMetric()
def roadExits(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "RoadOffset", "Velocity"]
    drivedata.checkColumns(required_col)

    # assuming a two lane road, determine the amount of time they were not in the legal roadway
    # Lane width 3.6m, car width 1.8m
    roadOutTime = 0
    outtimes = drivedata.data[(drivedata.data.RoadOffset > (7.2)) | (drivedata.data.RoadOffset < (0))
                                & (drivedata.data.Velocity > 1)]
    deltas = outtimes.diff()
    if deltas.shape[0] > 0:
        deltas.iloc[0] = deltas.iloc[1]
        roadOutTime += sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)])
    return roadOutTime

@registerMetric()
def roadExitsY(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "YPos", "Velocity"]
    drivedata.checkColumns(required_col)

    # assuming a two lane road, determine the amount of time they were not in the legal roadway
    # Lane width 3.6m, car width 1.8m
    roadOutTime = 0
    outtimes = drivedata.data[(drivedata.data.YPos > (7.2 - 0.9)) | (drivedata.data.YPos < (0 + 0.9))
                                & (drivedata.data.Velocity > 1)]
    deltas = outtimes.diff()
    if deltas.shape[0] > 0:
        deltas.iloc[0] = deltas.iloc[1]
        roadOutTime += sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)])
    return roadOutTime


# incomplete
def brakeJerk(drivedata: pydre.core.DriveData, cutoff: float = 0):
    required_col = ["SimTime", "LonAccel"]
    drivedata.checkColumns(required_col)

    a = []
    t = []
    df = pandas.DataFrame(drivedata.data, columns=required_col)  # drop other columns
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
@registerMetric()
def steeringEntropy(drivedata: pydre.core.DriveData, cutoff: float = 0):
    required_col = ["SimTime", "Steer"]
    drivedata.checkColumns(required_col)

    out = []
    df = pandas.DataFrame(drivedata.data, columns=required_col)  # drop other columns
    df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates

    if len(df) == 0:
        return None

    # resample data
    minTime = df.SimTime.values.min()
    maxTime = df.SimTime.values.max()
    nsteps = math.floor((maxTime - minTime) / 0.0167)  # divide into 0.0167s increments
    regTime = np.linspace(minTime, maxTime, num=nsteps)
    rsSteer = np.interp(regTime, df.SimTime, df.Steer)
    resampdf = np.column_stack((regTime, rsSteer))
    resampdf = pandas.DataFrame(resampdf, columns=("simTime", "rsSteerAngle"))

    # calculate predicted angle
    pAngle = (2.5 * df.Steer.values[3:, ]) - (2 * df.Steer.values[2:-1, ]) - (0.5 * df.Steer.values[1:-2, ])

    # calculate error
    error = df.Steer.values[3:, ] - pAngle
    out.append(error)

    # concatenate out (list of np objects) into a single list
    if len(out) == 0:
        return None
    error = np.concatenate(out)
    # 90th percentile of error
    alpha = np.nanpercentile(error, 90)

    # divide into 9 bins with edges: -5a,-2.5a,-a,a,2.5,5a
    binnedError = np.histogram(error, bins=[-10 * abs(alpha), -5 * abs(alpha), -2.5 * abs(alpha),
                                               -abs(alpha), -0.5 * abs(alpha), 0.5 * abs(alpha), abs(alpha),
                                               2.5 * abs(alpha), 5 * abs(alpha), 10 * abs(alpha)])

    # calculate H
    binnedArr = np.asarray(binnedError[0])
    binnedArr = binnedArr.astype(float)

    # check out calc of p
    p = np.divide(binnedArr, np.sum(binnedArr))
    Hp = np.multiply(np.multiply(-1, p), (np.log(p) / np.log(9)))
    Hp = Hp[~np.isnan(Hp)]
    Hp = np.sum(Hp)

    return Hp

@registerMetric()
def tailgatingTime(drivedata: pydre.core.DriveData, cutoff=2):
    tail_time = 0
    table = drivedata.data
    difftime = table.SimTime.values[1:] - table.SimTime.values[:-1]
    table.loc[:, 'delta_t'] = np.concatenate([np.zeros(1), difftime])
    # find all tailgating instances where the delta time is reasonable.
    # this ensures we don't get screwy data from merged files
    tail_data = table[(table.HeadwayTime > 0) & (table.HeadwayTime < cutoff) & (abs(table.delta_t) < .5)]
    tail_time += tail_data['delta_t'][abs(table.delta_t) < .5].sum()
    return tail_time

@registerMetric()
def tailgatingPercentage(drivedata: pydre.core.DriveData, cutoff: float = 2):
    total_time = 0
    tail_time = 0
    table = drivedata.data
    difftime = table.SimTime.values[1:] - table.SimTime.values[:-1]
    table.loc[:, 'delta_t'] = np.concatenate([np.zeros(1), difftime])
    # find all tailgating instances where the delta time is reasonable.
    # this ensures we don't get screwy data from merged files
    tail_data = table[(table.HeadwayTime > 0) & (table.HeadwayTime < cutoff) & (abs(table.delta_t) < .5)]
    tail_time += tail_data['delta_t'][abs(table.delta_t) < .5].sum()
    total_time += table['delta_t'][abs(table.delta_t) < .5].sum()
    return tail_time / total_time

@registerMetric()
def averageBoxReactionTime(drivedata: pydre.core.DriveData):
    required_col = ["ReactionTime"]
    diff = drivedata.checkColumns(required_col)
    df = drivedata.data
    df = df[df['ReactionTime'].notnull()]
    #Filter all reaction times that are negative (missed boxes) then output mean
    return df[df["ReactionTime"] > 0.0]["ReactionTime"].mean()

@registerMetric()
def sdBoxReactionTime(drivedata: pydre.core.DriveData):
    required_col = ["ReactionTime"]
    diff = drivedata.checkColumns(required_col)
    df = drivedata.data
    df = df[df['ReactionTime'].notnull()]
    #Filter all reaction times that are negative (missed boxes) then output sd
    return df[df["ReactionTime"] > 0.0]["ReactionTime"].std()

#cutoff: represents the time in seconds the reaction time should be within for a "Hit"
def countBoxHits(drivedata: pydre.core.DriveData, cutoff = 5):
    required_col = ["ReactionTime"]
    diff = drivedata.checkColumns(required_col)
    df = drivedata.data
    df = df[df['ReactionTime'].notnull()]
    #return number of hits within cutoff
    return df[(df['ReactionTime'] > 0) & (df['ReactionTime'] < cutoff)].shape[0]

#cutoff: represents the time in seconds the reaction time should be within for a "Hit"
def percentBoxHits(drivedata: pydre.core.DriveData, cutoff = 5):
    required_col = ["ReactionTime"]
    diff = drivedata.checkColumns(required_col)
    df = drivedata.data
    df = df[df['ReactionTime'].notnull()]
    #return percentage of hits within cutoff
    return ((df[(df['ReactionTime'] > 0) & (df['ReactionTime'] < cutoff)].shape[0]) / (df.shape[0])) * 100

def countBoxMisses(drivedata: pydre.core.DriveData):
    required_col = ["ReactionTime"]
    diff = drivedata.checkColumns(required_col)
    df = drivedata.data
    df = df[df['ReactionTime'].notnull()]
    #return number of negative reation Times (indicates box was missed)
    return df[(df['ReactionTime'] < 0)].shape[0]

def percentBoxMisses(drivedata: pydre.core.DriveData):
    required_col = ["ReactionTime"]
    diff = drivedata.checkColumns(required_col)
    df = drivedata.data
    df = df[df['ReactionTime'].notnull()]
    #return percentage of Misses
    return ((df[(df['ReactionTime'] < 0)].shape[0]) / (df.shape[0])) * 100

@registerMetric()
def boxMetrics(drivedata: pydre.core.DriveData, cutoff: float = 0, stat: str = "count"):
    required_col = ["SimTime", "FeedbackButton", "BoxAppears"]
    diff = drivedata.checkColumns(required_col)

    total_boxclicks = pandas.Series(dtype='float64')
    # original code here: total_boxclicks = pandas.Series()
    # Got this warning on pandas 1.2.4: " DeprecationWarning: The default dtype for empty Series will be 'object' 
    # instead of 'float64' in a future version. Specify a dtype explicitly to silence this warning."
    # Plz change it back to the original code if the current one leads to an issue
    time_boxappeared = 0.0
    time_buttonclicked = 0.0
    hitButton = 0
    df = pandas.DataFrame(drivedata.data, columns=required_col)  # drop other columns
    df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
    if len(df) == 0:
        return None
    boxAppearsdf = df['BoxAppears']
    simTimedf = df['SimTime']
    boxOndf = boxAppearsdf.diff(1)
    indicesBoxOn = boxOndf[boxOndf.values > .5].index[0:]
    indicesBoxOff = boxOndf[boxOndf.values < 0.0].index[0:]
    feedbackButtondf = df['FeedbackButton']
    reactionTimeList = list()
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
                endIndex = counter + 1
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
        mean = np.mean(reactionTimeList, axis=0)
        return mean
    elif stat == "sd":
        sd = np.std(reactionTimeList, axis=0)
        return sd
    else:
        print("Can't calculate that statistic.")
    return hitButton

@registerMetric()
def firstOccurrence(df: pandas.DataFrame, condition: str):
    try:
        output = df[condition].head(1)
        return output.index[0]
    except:
        return None

@registerMetric()
def timeFirstTrue(drivedata: pydre.core.DriveData, var: str):
    required_col = [var, "SimTime"]
    diff = drivedata.checkColumns(required_col)
    if drivedata.data[var].max() == 0:
        return np.nan
    try:
        f = drivedata.data[var].idxmax()
        return drivedata.data["SimTime"].loc[f] - drivedata.data["SimTime"].iloc[0]
    except ValueError:
        return None

@registerMetric()
def reactionBrakeFirstTrue(drivedata: pydre.core.DriveData, var:str):
    required_col = [var, "SimTime"]
    diff = drivedata.checkColumns(required_col)
    if drivedata.data[var].max() == 0:
        return np.nan
    try:
        f = drivedata.data[drivedata.data[var].gt(5)].index[0]
        return drivedata.data["SimTime"].loc[f] - drivedata.data["SimTime"].iloc[0]
    except ValueError:
        return None

@registerMetric()
def reactionTimeEventTrue(drivedata: pydre.core.DriveData, var:str):
    required_col = [var, "SimTime"]
    diff = drivedata.checkColumns(required_col)
    if drivedata.data[var].min() != -1:
        return np.nan
    try:
        f = drivedata.data[var].idxmin()
        return drivedata.data["SimTime"].loc[f] - drivedata.data["SimTime"].iloc[0]
    except ValueError:
        return None

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

@registerMetric()
def tbiReaction(drivedata: pydre.core.DriveData, type: str = "brake", index: int = 0):
    required_col = ["SimTime", "Brake", "Throttle", "MapHalf", "MapSectionLocatedIn", "HazardActivation"]
    diff = drivedata.checkColumns(required_col)

    df = pandas.DataFrame(drivedata.data, columns=(required_col))
    df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
    if len(df) == 0:
        return None

    reactionTimes = []
    simtime = df['SimTime']
    hazard = df['HazardActivation']

    hazardIndex = [1, 3][index]
    if type == "brake":
        # brakesd = np.std(df.Brake)
        start = firstOccurrence(df, hazard == hazardIndex)
        if start:
            startTime = df["SimTime"].loc[start]
            startBrake = df["Brake"].loc[start]
            # check maximum of 10 seconds from hazard activation
            reactionTime = firstOccurrence(df, (simtime > startTime)  # after the starting of the hazard
                                           & (simtime < startTime + 10)  # before 10 seconds after the hazard
                                           & (df["Brake"] > startBrake + 0.5))
            if reactionTime:
                print(
                    "hazard {} reactiontime {}".format(hazardIndex, simtime.loc[reactionTime] - simtime.loc[start]))
                reactionTimes.append(simtime.loc[reactionTime] - simtime.loc[start])
    elif type == "throttle":
        throttlesd = np.std(df[(hazard == 0) | (hazard == 2)].Throttle)
        throttlediff = df["Throttle"].diff()
        start = firstOccurrence(df, hazard == hazardIndex)
        if start:
            startTime = df["SimTime"].loc[start]
            reactionTime = firstOccurrence(df, (simtime > startTime)  # after the starting of the hazard
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

@registerMetric()
def ecoCar(drivedata: pydre.core.DriveData, FailCode: str = "1", stat: str = "mean"):
    required_col = ["SimTime", "WarningToggle", "FailureCode", "Throttle", "Brake", "Steer", "AutonomousDriving"]
    diff = drivedata.checkColumns(required_col)

    event = 0
    df = pandas.DataFrame(drivedata.data, columns=(required_col))  # drop other columns
    df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates

    if (len(df) == 0):
        return None

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
            mean = np.mean(reactionTimeList, axis=0)
        return mean
    elif stat == "sd":
        sd = None
        if (len(reactionTimeList) > 0):
            sd = np.std(reactionTimeList, axis=0)
        return sd
    elif stat == "event":
        return len(reactionTimeList)
    else:
        print("Can't calculate that statistic.")

