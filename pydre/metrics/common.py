from __future__ import annotations  # needed for python < 3.9

from typing import Optional

import logging
import re

import pandas
import polars as pl

import pydre.core
from pydre.metrics import registerMetric
import numpy as np
import math

# metrics defined here take a list of DriveData objects and return a single floating point value

# not registered & incomplete

logger = logging.getLogger(__name__)


# @registerMetric()
# def findFirstTimeAboveVel(drivedata: pydre.core.DriveData, cutoff: float = 25):
#     required_col = ["Velocity"]
#     drivedata.checkColumns(required_col)
#     timestepID = -1
#     # TODO: reimplement with selection and .head(1)
#
#     for i, row in drivedata.data.iterrows():
#         if row.Velocity >= cutoff:
#             timestepID = i
#             break
#
#     return timestepID


# def findFirstTimeOutside(drivedata: pydre.core.DriveData, area: list[float] = (0, 0, 10000, 10000)):
# TODO: implement with selection and .head(1)


# helper func - check if a series only contains 0
def checkSeriesNan(series: polars.Series):
    unq = series.unique().sort()
    if unq.size == 1:
        if unq[0] == 0:
            return True
    return False

@registerMetric()
def colMean(drivedata: pydre.core.DriveData, var: str, cutoff: Optional[float] = None):
    required_col = [var]
    drivedata.checkColumns(required_col)
    if cutoff is not None:
        return drivedata.data.get_column(var).filter(drivedata.data.get_column(var) >= cutoff).mean()
    else:
        return drivedata.data.get_column(var).mean()

@registerMetric()
def colSD(drivedata: pydre.core.DriveData, var: str, cutoff: Optional[float] = None):
    required_col = [var]
    drivedata.checkColumns(required_col)
    if cutoff is not None:
        return drivedata.data.get_column(var).filter(drivedata.data.get_column(var) >= cutoff).std()
    else:
        return drivedata.data.get_column(var).std()

@registerMetric()
def colMax(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    drivedata.checkColumns(required_col)
    return drivedata.data.get_column(var).max()

@registerMetric()
def colMin(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    drivedata.checkColumns(required_col)
    return drivedata.data.get_column(var).min()

@registerMetric()
def colFirst(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    drivedata.checkColumns(required_col)
    return drivedata.data.get_column(var).head(1).item()

@registerMetric()
def colLast(drivedata: pydre.core.DriveData, var: str):
    required_col = [var]
    drivedata.checkColumns(required_col)
    return drivedata.data.get_column(var).tail(1).item()

@registerMetric()
def timeAboveSpeed(drivedata: pydre.core.DriveData, cutoff: float = 0, percentage: bool = False):
    required_col = ["SimTime", "Velocity"]
    drivedata.checkColumns(required_col)

    df = drivedata.data.select( [pl.col("SimTime"),
                                 pl.col("Velocity"),
                                 pl.col("SimTime").diff().clip_min(0).alias("Duration")
                                 ])

    time = df.get_column("Duration").filter(df.get_column("Velocity") >= cutoff).sum()
    total_time = df.get_column("SimTime").max() - df.get_column("SimTime").min()
    if percentage:
        out = time / total_time
    else:
        out = time
    return out

@registerMetric()
def timeWithinRange(drivedata: pydre.core.DriveData, lowerlimit: int, upperlimit: int, percentage: bool = False):
    required_col = ["SimTime", "Velocity"]
    drivedata.checkColumns(required_col)

    df = drivedata.data.select( [pl.col("SimTime"),
                                 pl.col("Velocity"),
                                 pl.col("SimTime").diff().clip_min(0).alias("Duration")
                                 ])

    time = (df.get_column("Duration").filter( (df.get_column("Velocity") < upperlimit) &
                                              (df.get_column("Velocity") >= lowerlimit)).sum())

    if percentage:
        total_time = df.get_column("SimTime").max() - df.get_column("SimTime").min()
        out = time / total_time
    else:
        out = time
    return out

@registerMetric()
def stoppingDist(drivedata : pydre.core.DriveData, roadtravelposition = "XPos"):
    required_col = [roadtravelposition, "Velocity"]
    drivedata.checkColumns(required_col)

    df = drivedata.data.select( [pl.col(roadtravelposition),
                                 pl.col("Velocity")] )

    minvelocity = df.get_column("Velocity").min()
    stopposition = df.filter(pl.col("Velocity") == minvelocity).get_column(roadtravelposition).min()

    lineposition = (df.get_column(roadtravelposition).min() + df.get_column(roadtravelposition).max()) / 2
    distfromline = lineposition - stopposition

    if ()

# Lane metrics


# laneExits
# Will compute the number of transitions from the lane number specified to (lane+1) or (lane-1)
# the 'sign' function will remove transitions from (lane+1) to (lane+2) or similar
@registerMetric()
def laneExits(drivedata: pydre.core.DriveData, lane=2, lane_column = "Lane"):
    drivedata.checkColumns([lane_column, ])
    return drivedata.data.select((pl.col(lane_column) - lane).sign().diff().abs()).sum().item()


def laneViolations(drivedata: pydre.core.DriveData, offset: str = "LaneOffset",
                   lane: int = 2, lane_column: str = "Lane",
                   lane_width: float = 3.65, car_width: float = 2.1):
    drivedata.checkColumns([lane_column, ])
    # tolerance is the maximum allowable offset deviation from 0
    tolerance = lane_width / 2 - car_width / 2
    lane_data = drivedata.data.filter(pl.col(lane_column) == 2)
    is_violating = lane_data.get_column(offset).abs() > tolerance
    return is_violating.diff().clip_min(0).sum()

def laneViolationDuration(drivedata: pydre.core.DriveData, offset: str = "LaneOffset",
                   lane: int = 2, lane_column: str = "Lane",
                   lane_width: float = 3.65, car_width: float = 2.1):

    tolerance = lane_width / 2 - car_width / 2
    lane_data = drivedata.data.filter(pl.col(lane_column) == 2)
    lane_data = lane_data.select([pl.col(offset).abs().alias("LaneViolations") > tolerance,
                                  pl.col("SimTime").diff().clip_min(0).alias("Duration")
    ])

    return lane_data.select(pl.col("LaneViolations") * pl.col("Duration")).sum().item()

# Parameters:

# Offset: the name of the specific column in the datafile, could be LaneOffset or RoadOffset

# noisy: If this is set to 'true', a low pass filter with 5 Hz cut off frequency will be applied, according to documentation
# The document doesn't specify the order of filter so I'll use 1st order here

# filfilt: if this is set to 'true', the filter will be applied twice, once forward and once backwards. This gives better results
# when testing with a sin signal, but I'm not sure if that leads to a risk or not so I'll keep that as an option

# noisy and filtfilt are NOT case sensitive and are meaningful only when calculating MSDLP
# @registerMetric()
# def lanePosition(drivedata: pydre.core.DriveData, laneInfo: str = "sdlp", lane=2, lane_width: float = 3.65,
#                  car_width: float = 2.1,
#                  offset: str = "LaneOffset", noisy="false", filtfilt="false"):
#     required_col = ["SimTime", "DatTime", "Lane", offset]
#     drivedata.checkColumns(required_col)
#
#     df = pandas.DataFrame(drivedata.data, columns=required_col)  # drop other columns
#     LPout = None
#     if (df.size > 0):
#         if (laneInfo in ["mean", "Mean"]):
#             # mean lane position
#             LPout = np.mean((df[offset]))  # abs to give mean lane "error"
#         elif (laneInfo in ["msdlp", "MSDLP"]):
#             samplingFrequency = 1 / np.mean(np.diff(df.DatTime))  # calculate sampling drequency based on DatTime
#             # samplingFrequency = 1 / np.mean(np.diff(df.SimTime))
#
#             sos = signal.butter(2, 0.1, 'high', analog=False, output='sos',
#                                 fs=float(samplingFrequency))  # define butterWorthFilter
#             # the output parameter can also be set to 'ba'. Under this case, signal.lfilter(b, a, array) or
#             # signal.filtfilt(b, a, array) should be used. sos is recommanded for general purpose filtering
#
#             data = df[offset]
#             if (noisy.lower() == "true"):
#                 sosLow = signal.butter(1, 5, 'low', analog=False, output='sos', fs=float(samplingFrequency))
#                 data = signal.sosfilt(sosLow, data)
#                 # apply a low pass filter to reduce the noise
#
#             filteredLP = None
#             if (filtfilt.lower() == "true"):
#                 filteredLP = signal.sosfiltfilt(sos, data)  # apply the filter twice
#             else:
#                 filteredLP = signal.sosfilt(sos, data)  # apply the filter once
#             # signal.sosfiltfilt() applies the filter twice (forward & backward) while signal.sosfilt applies
#             # the filter once.
#
#             LPout = np.std(filteredLP)
#
#         elif (laneInfo in ["sdlp", "SDLP"]):
#             LPout = np.std(df[offset])
#             # Just cause I've been staring at this a while and want to get some code down:
#             # Explanation behind this: SAE recommends using the unbiased estimator "1/n-1". The np code does
#             # not use this, so I wrote up code that can easily be subbed in, if it's determined necessary.
#             """
#             entrynum = len(df[offset])
#             unbiased_estimator = 1/(entrynum - 1)
#             average = np.mean((df[offset]))
#             variation = 0
#             for entry in entrynum:
#                 variation += (pow(df[offset][entry] - average, 2))
#             LPout = math.sqrt(unbiased_estimator * variation)
#             """
#         elif (laneInfo in ["exits"]):
#             LPout = (df.Lane - df.Lane.shift(1)).abs().sum()
#         elif (laneInfo in ["violation_count"]):
#             LPout = 0
#             # tolerance is the maximum allowable offset deviation from 0
#             tolerance = lane_width / 2 - car_width / 2
#             is_violating = abs(df[offset]) > tolerance
#
#             # Shift the is_violating array and look for differences.
#             shifted = is_violating.shift(1)
#             shifted.iloc[0] = is_violating.iloc[0]
#
#             # Create an array which is true whenever the car goes in/out of
#             # the lane
#             compare = shifted != is_violating
#
#             # shiftout becomes an array which only has elements each time
#             # compare is true (ie, violation status changed). These elements
#             # are True when the direction is out of the lane, False when the
#             # direction is back into the lane. We only count the out shifts.
#             shifts = compare.loc[compare == True] == is_violating.loc[compare == True]
#             shiftout = shifts.loc[shifts == True]
#
#             # Count all violations. Add one if the region begins with a violation.
#             if is_violating.iloc[0] is True:
#                 LPout = LPout + 1
#             LPout = LPout + shiftout.size
#
#         elif laneInfo in ["violation_duration"]:
#             LPout = 0
#             tolerance = lane_width / 2 - car_width / 2
#             violations = df[abs(df[offset]) > tolerance]
#             if (violations.size > 0):
#                 deltas = violations.diff()
#                 deltas.iloc[0] = deltas.iloc[1]
#                 LPout = sum(deltas.SimTime[(deltas.SimTime < .5) & (deltas.SimTime > 0)])
#         else:
#             print("Not a valid lane position metric - use 'mean', 'sdlp', or 'exits'.")
#             return None
#     return LPout

@registerMetric()
def roadExits(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "RoadOffset", "Velocity"]
    drivedata.checkColumns(required_col)

    # assuming a two lane road, determine the amount of time they were not in the legal roadway
    # Lane width 3.6m, car width 1.8m

    df = drivedata.data.select([
        pl.col("SimTime"),
        pl.col("RoadOffset"),
        pl.col("Velocity"),
        pl.col("SimTime").diff().alias("Duration").clip(0, 0.5)  # any duration outside this range is bad data (maybe from a splice)
    ])

    outtimes = df.filter(
        pl.col("RoadOffset").is_between(0, 7.2).is_not() & (pl.col("Velocity") > 1)
    )

    return outtimes.get_column("Duration").sum()

@registerMetric()
def roadExitsY(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "YPos", "Velocity"]
    drivedata.checkColumns(required_col)

    # assuming a two lane road, determine the amount of time they were not in the legal roadway
    # Lane width 3.6m, car width 1.8m

    df = drivedata.data.select([
        pl.col("SimTime"),
        pl.col("RoadOffset"),
        pl.col("Velocity"),
        pl.col("SimTime").diff().alias("Duration").clip(0, 0.5)  # any duration outside this range is bad data (maybe from a splice)
    ])

    outtimes = df.filter(
        pl.col("RoadOffset").is_between(0+0.9, 7.2 - 0.9).is_not() & (pl.col("Velocity") > 1)
        # TODO: double check offsets
    )

    return outtimes.get_column("Duration").sum()

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
    tailgating_table = drivedata.data.select([pl.col("SimTime").diff().alias("delta_t"),
                                              pl.col("HeadwayTime")])
    # find all tailgating instances where the delta time is reasonable.
    # this ensures we don't get screwy data from merged files
    tail_time += tailgating_table.filter(pl.col("HeadwayTime").is_between(0, cutoff, closed="none") &
                                         pl.col("delta_t").is_between(0, .5)).select("delta_t").sum().item()
    return tail_time

@registerMetric()
def tailgatingPercentage(drivedata: pydre.core.DriveData, cutoff: float = 2):
    tail_time = 0
    total_time = 0
    tailgating_table = drivedata.data.select([pl.col("SimTime").diff().alias("delta_t"),
                                              pl.col("HeadwayTime")])
    # find all tailgating instances where the delta time is reasonable.
    # this ensures we don't get screwy data from merged files
    tail_time += tailgating_table.filter(pl.col("HeadwayTime").is_between(0, cutoff, closed="none") &
                                         pl.col("delta_t").is_between(0, .5)).select("delta_t").sum().item()
    total_time += tailgating_table.filter(pl.col("delta_t").is_between(0, .5)).select("delta_t").sum().item()
    return tail_time / total_time

@registerMetric()
def tailgatingPercentageAboveSpeed(drivedata: pydre.core.DriveData, cutoff: float =2, velocity: float = 13.4112):
    tail_time = 0
    total_time = 0
    tailgating_table = drivedata.data.select([pl.col("SimTime").diff().alias("delta_t"),
                                              pl.col("HeadwayTime"),
                                              pl.col("Velocity")]).filter(pl.col("Velocity") >= velocity)
    # find all tailgating instances where the delta time is reasonable.
    # this ensures we don't get screwy data from merged files
    tail_time += tailgating_table.filter(pl.col("HeadwayTime").is_between(0, cutoff, closed="none") &
                                         pl.col("delta_t").is_between(0, .5)).select("delta_t").sum().item()
    total_time += tailgating_table.filter(pl.col("delta_t").is_between(0, .5)).select("delta_t").sum().item()
    return tail_time / total_time


# determines when the ownship collides with another vehicle by examining headway distance as threshold
@registerMetric()
def leadVehicleCollision(drivedata: pydre.core.DriveData, cutoff: float = 2.85):
    required_col = ["SimTime", "HeadwayDistance"]
    drivedata.checkColumns(required_col)
    # find contiguous instances of headway distance < the cutoff
    collision_table = drivedata.data.select((pl.col("HeadwayDistance") <= cutoff).alias("CollisionZone"))
    collisions = collision_table.select(pl.col("CollisionZone").cast(pl.Int32).diff()).sum().item()
    return collisions


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
    try:
        df = drivedata.data.filter(pl.col(var) > 0)
    except pl.exceptions.ComputeError as e:
        logger.warning("Failure processing timeFirstTrue metric for variable {} in file {}".format(var, drivedata.sourcefilename))
        return None
    if drivedata.data.height == 0 or df.height == 0:
        return None
    return df.select("SimTime").head(1).item() - drivedata.data.select("SimTime").head(1).item()


@registerMetric()
def reactionBrakeFirstTrue(drivedata: pydre.core.DriveData, var:str):
    required_col = [var, "SimTime"]
    diff = drivedata.checkColumns(required_col)
    try:
        df = drivedata.data.filter(pl.col(var) > 5)
    except pl.exceptions.ComputeError as e:
        logger.warning("Brake value non-numeric in {}".format(drivedata.sourcefilename))
        return None
    if drivedata.data.height == 0 or df.height == 0:
        return None
    return df.select("SimTime").head(1).item() - drivedata.data.select("SimTime").head(1).item()

@registerMetric()
def reactionTimeEventTrue(drivedata: pydre.core.DriveData, var1:str, var2:str):
    required_col = [var1, var2, "SimTime"]
    diff = drivedata.checkColumns(required_col)
    break_reaction = reactionBrakeFirstTrue(drivedata, var1)

    if break_reaction:
        return break_reaction
    else:
        df = drivedata.data.filter(abs(pl.col(var2)) >= .2)
        if drivedata.data.height == 0 or df.height == 0:
            return None
        return df.select("SimTime").head(1).item() - drivedata.data.select("SimTime").head(1).item()
    

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

# @registerMetric()
# def ecoCar(drivedata: pydre.core.DriveData, FailCode: str = "1", stat: str = "mean"):
#     required_col = ["SimTime", "WarningToggle", "FailureCode", "Throttle", "Brake", "Steer", "AutonomousDriving"]
#     diff = drivedata.checkColumns(required_col)
#
#     event = 0
#     df = pandas.DataFrame(drivedata.data, columns=(required_col))  # drop other columns
#     df = pandas.DataFrame.drop_duplicates(df.dropna(axis=0, how='any'))  # remove nans and drop duplicates
#
#     if (len(df) == 0):
#         return None
#
#     warningToggledf = df['WarningToggle']
#     autonomousToggledf = df['AutonomousDriving']
#     throttledf = df['Throttle']
#     brakedf = df['Brake']
#     steerdf = df['Steer']
#     simTimedf = df['SimTime']
#     failureCodedf = df["FailureCode"]
#
#     toggleOndf = warningToggledf.diff(1)
#     indicesToggleOn = toggleOndf[toggleOndf.values > .5].index[0:]
#     indicesToggleOff = toggleOndf[toggleOndf.values < 0.0].index[0:]
#
#     reactionTimeList = list()
#
#     for counter in range(0, len(indicesToggleOn)):
#
#         warningOn = int(indicesToggleOn[counter])
#         startWarning = simTimedf.loc[warningOn]
#         ## End time (start of warning time plus 15 seconds)
#         warningPlus15 = df[(df.SimTime >= startWarning) & (df.SimTime <= startWarning + 15)]
#         indWarning = warningPlus15.index[0:]
#
#         warningOff = int(indWarning[-1])
#         endTime = simTimedf.loc[warningOff]
#
#         if (failureCodedf.loc[warningOn] == int(FailCode)):
#
#             rtList = list()
#             ## Compare brake, throttle & steer
#
#             # Brake Reaction
#             brakeDuringWarning = brakedf.loc[warningOn:warningOff]
#             reaction_Brake = 0
#             initial_Brake = brakeDuringWarning.iloc[0]
#             thresholdBrake = 2
#             brakeVector = brakeDuringWarning[brakeDuringWarning >= (initial_Brake + thresholdBrake)]
#             if (len(brakeVector > 0)):
#                 brakeValue = brakeVector.iloc[0]
#                 indexB = brakeVector.index[0]
#                 reaction_Brake = simTimedf[indexB] - startWarning
#             if (reaction_Brake > 0):
#                 rtList.append(reaction_Brake)
#
#             ## Throttle Reaction
#             throttleDuringWarning = throttledf.loc[warningOn:warningOff]
#             reaction_throttle = 0
#             initial_throttle = throttleDuringWarning.iloc[0]
#             thresholdThrottle = 2
#             throttleVector = throttleDuringWarning[throttleDuringWarning >= (initial_throttle + thresholdThrottle)]
#             if (len(throttleVector > 0)):
#                 throttleValue = throttleVector.iloc[0]
#                 indexT = throttleVector.index[0]
#                 reaction_throttle = simTimedf[indexT] - startWarning
#             if (reaction_throttle > 0):
#                 rtList.append(reaction_throttle)
#
#             ## Steer Reaction
#             steerDuringWarning = steerdf.loc[warningOn:warningOff]
#             reaction_steer = 0
#             thresholdSteer = 2
#             initial_steer = steerDuringWarning.iloc[0]
#             steerVector = steerDuringWarning[(steerDuringWarning >= (initial_steer + thresholdSteer))]
#             steerVector2 = steerDuringWarning[(steerDuringWarning <= (initial_steer - thresholdSteer))]
#             steerVector.append(steerVector2)
#             if (len(steerVector > 0)):
#                 steerValue = steerVector.iloc[0]
#                 indexS = steerVector.index[0]
#                 reaction_steer = simTimedf[indexS] - startWarning
#
#             if (reaction_steer > 0):
#                 rtList.append(reaction_steer)
#
#             # Reaction By Toggling Autonomous Back On
#             autonomousDuringWarning = autonomousToggledf.loc[warningOn:warningOff]
#             reaction_autonomous = 0
#             autonomousOndf = autonomousDuringWarning.diff(1)
#             autonomousToggleOn = autonomousOndf[autonomousOndf.values > .5].index[0:]
#             if (len(autonomousToggleOn) > 0):
#                 indexA = int(autonomousToggleOn[0])
#                 reaction_autonomous = simTimedf[indexA] - startWarning
#
#             if (reaction_autonomous > 0):
#                 rtList.append(reaction_autonomous)
#
#             # Compare all Reaction Times
#             if (len(rtList) != 0):
#                 reactionTime = min(rtList)
#                 reactionTimeList.append(reactionTime)
#
#     reactionTimeList = [x for x in reactionTimeList if x != None]
#
#     if stat == "mean":
#         mean = None
#         if (len(reactionTimeList) > 0):
#             mean = np.mean(reactionTimeList, axis=0)
#         return mean
#     elif stat == "sd":
#         sd = None
#         if (len(reactionTimeList) > 0):
#             sd = np.std(reactionTimeList, axis=0)
#         return sd
#     elif stat == "event":
#         return len(reactionTimeList)
#     else:
#         print("Can't calculate that statistic.")

@registerMetric("R2DIDColumns", ["ParticipantID", "MatchID", "Case", "Location", "Gender", "Week"])
def R2DIDColumns(drivedata: pydre.core.DriveData):
    ident = drivedata.PartID
    ident_groups = re.match(r'(\d)(\d)(\d)(\d\d\d\d)[wW](\d)', ident)
    if ident_groups is None:
        logger.warning("Could not parse R2D ID " + ident)
        return [None, None, None, None, None, None]
    participant_id = ident_groups.group(1) + ident_groups.group(2) + ident_groups.group(3) + ident_groups.group(4)
    case = ident_groups.group(1)
    if case == "3":
        case = "Case"
    elif case == "5":
        case = "Control"
    elif case == "7":
        case = "Enrolled"
    location = ident_groups.group(2)
    if location == "1":
        location = "UAB"
    elif location == "2":
        location = "OSU"
    gender = ident_groups.group(3)
    if gender == "1":
        gender = "Male"
    elif gender == "2":
        gender = "Female"
    match_id = ident_groups.group(4)
    week = ident_groups.group(5)
    return participant_id, match_id, case, location, gender, week
