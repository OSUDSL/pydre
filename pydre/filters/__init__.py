import polars as pl
import pandas

import pydre.core
import numpy as np
import logging
import os
import datetime
import struct

import typing
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


filtersList = {}
filtersColNames = {}


def registerFilter(jsonname=None, columnnames=None):
    def registering_decorator(func):
        jname = jsonname
        if not jname:
            jname = func.__name__
        # register function
        filtersList[jname] = func
        if columnnames:
            filtersColNames[jname] = columnnames
        else:
            filtersColNames[jname] = [jname, ]
        return func
    return registering_decorator


# filters defined here take a DriveData object and return an updated DriveData object

# @registerFilter()
# def boxIdentificationTime(drivedata: pydre.core.DriveData, button_column="ResponseButton"):
#     #check if required column names for mesopic study
#     required_col = ["SimTime", "BoxStatus", button_column]
#     diff = drivedata.checkColumns(required_col)
#
#     df = pl.select(pl.col(required_col))
#     df.unique()
#
#     df = df.select(
#         [
#             pl.col("*"),  # select all
#             pl.col("BoxStatus").diff(1, "ignore").alias("BoxStatusChanges"),
#             pl.col(button_column).alias("BoxButtonResponse")
#         ])
#
#
#     df = pandas.DataFrame(drivedata.data)
#     dt = pandas.DataFrame(df, columns=required_col)  # drop other columns
#     dt = pandas.DataFrame.drop_duplicates(dt.dropna(axis=0, how='any'))  # remove nans and drop duplicates
#     #Get DataFrame object and specific columns in data frame
#     time = dt["SimTime"]
#     boxStatus = dt["BoxStatus"]
#     response = dt[button_column]
#     #Subtract with previous row value to find the start times of each box
#     boxStatus = boxStatus.diff(1)
#     #Get the specific row indices of the start times for each box
#     boxOnStart = boxStatus[boxStatus.values > 0.5].index[0:]
#     #List to Hold the user reaction Time for indentifiying boxes
#     reactionTime = list()
#     #Iterate through the box start time indices
#     for i in range(0, len(boxOnStart)):
#         #Get the actual start time for when the box first starts appearing
#         startTime = time.loc[boxOnStart[i]]
#         #Find when user (if any) pressed response
#         if i == len(boxOnStart) - 1:
#             detected = response.loc[boxOnStart[i]:].diff(1)
#         else:
#             detected = response.loc[boxOnStart[i]:boxOnStart[i+1]].diff(1)
#         #Get the detected indexes of when user (if any) pressed response button for the specific box
#         detectedIndices = detected[detected.values > 0.5].index[0:]
#         #if no response then append negative result
#         if len(detectedIndices) == 0:
#             reactionTime.append(-1)
#         else:
#             pressTime = time.loc[detectedIndices[0]]
#             #Append the reaction time from subtracting start time from when user presses response button first
#             reactionTime.append(pressTime - startTime)
#     #Concat to data frame
#     reactionTimeFrame = pandas.DataFrame({'ReactionTime': reactionTime})
#     dt = pandas.concat([dt, reactionTimeFrame], ignore_index=True)
#     #update drivedata data
#     drivedata.data["ReactionTime"] = dt["ReactionTime"]
#     #return drivedata object
#     return drivedata


@registerFilter()
def numberBinaryBlocks(drivedata: pydre.core.DriveData, binary_column="ButtonStatus", new_column="NumberedBlocks",
                       only_on=0, fill_after_block=0):
    required_col = [binary_column]
    diff = drivedata.checkColumns(required_col)

    blocks = drivedata.data.select(
            (pl.col(binary_column).shift() != pl.col(binary_column)).cumsum().alias(new_column)
    )
    blocks.fill_null(strategy="forward", limit=fill_after_block)
    drivedata.data.hstack(blocks, in_place=True)
    if only_on:
        try:
            drivedata.data = drivedata.data.filter(pl.col(binary_column) == 1)
        except pl.exceptions.ComputeError as e:
            logger.warning("Assumed binary column {} in {} has non-numeric value.".format(binary_column, drivedata.sourcefilename))
    return drivedata

@registerFilter()
def SimTimeFromDatTime(drivedata: pydre.core.DriveData):
    if drivedata.data.get_column("SimTime").max() == 0:
        drivedata.data.replace("SimTime", drivedata.data.get_column("DatTime"))
    return drivedata


@registerFilter()
def R2DFixReversedRoad(drivedata: pydre.core.DriveData):
    drivedata.data = drivedata.data.with_columns(pl.when(pl.col("XPos").cast(pl.Float32).is_between(700, 900)).
                                                 then(-(pl.col("RoadOffset").cast(pl.Float32))).
                                                 otherwise(pl.col("RoadOffset").cast(pl.Float32)).alias("RoadOffset"))
    return drivedata

@registerFilter()
def setinrange(drivedata: pydre.core.DriveData, coltoset:str, valtoset:float, colforrange:str,
               rangemin:float, rangemax:float):
    drivedata.data = drivedata.data.with_columns(pl.when(
        pl.col(colforrange).cast(pl.Float32).is_between(rangemin, rangemax)).then(
            valtoset).otherwise(pl.col(coltoset)).cast(pl.Float32).alias(coltoset))

    return drivedata


@registerFilter()
def relativeBoxPos(drivedata: pydre.core.DriveData):
    start_x = drivedata.data.get_column("XPos").min()
    drivedata.data = drivedata.data.with_columns([(pl.col("BoxPosY").cast(pl.Float32) - start_x).clip_min(0).alias("relativeBoxStart")])
    return drivedata

@registerFilter()
def smoothGazeData(drivedata: pydre.core.DriveData, timeColName: str = "DatTime",
                   gazeColName: str = "FILTERED_GAZE_OBJ_NAME", latencyShift=6):

    # Right now this is just converting to a pandas DataFrame, doing the old computation and converting back
    # TODO: convert to actually use polars

    required_col = [timeColName, gazeColName]
    diff = drivedata.checkColumns(required_col)

    dt = drivedata.data.to_pandas()
    cat_type = CategoricalDtype(
        categories=['None', 'localCS.dashPlane', 'localCS.WindScreen', 'localCS.CSLowScreen', 'onroad', 'offroad'])
    dt['gaze'] = dt[gazeColName].astype(cat_type)

    # dt['gaze'].replace(['None', 'car.dashPlane', 'car.WindScreen'], ['offroad', 'offroad', 'onroad'], inplace=True)
    dt['gaze'].replace(['None', 'localCS.dashPlane', 'localCS.WindScreen', 'localCS.CSLowScreen'],
                       ['offroad', 'offroad', 'onroad', 'offroad'], inplace=True)

    if len(dt['gaze'].unique()) < 2:
        print("Bad gaze data, not enough variety. Aborting")
        return None

    # smooth frame blips
    gaze_same = (dt['gaze'].shift(-1) == dt['gaze'].shift(1)) & (dt['gaze'].shift(-2) == dt['gaze'].shift(2)) & (
            dt['gaze'].shift(-2) == dt['gaze'].shift(-1)) & (dt['gaze'] != dt['gaze'].shift(1))
    # print("{} frame blips".format(gaze_same.sum()))
    dt.loc[gaze_same, 'gaze'] = dt['gaze'].shift(-1)

    # adjust for 100ms latency
    dt['gaze'] = dt['gaze'].shift(-latencyShift)
    dt['timedelta'] = pandas.to_timedelta(dt[timeColName].astype(float), unit="s")
    dt.set_index('timedelta', inplace=True)

    # filter out noise from the gaze column
    # SAE J2396 defines fixations as at least 0.2 seconds,
    min_delta = pandas.to_timedelta(0.2, unit='s')
    # so we ignore changes in gaze that are less than that

    # find list of runs
    dt['gazenum'] = (dt['gaze'].shift(1) != dt['gaze']).astype(int).cumsum()
    n = dt['gazenum'].max()
    dt = dt.reset_index()
    # breakpoint()
    durations = dt.groupby('gazenum')['timedelta'].max() - dt.groupby('gazenum')['timedelta'].min()

    # print("{} gazes before removing transitions".format(n))
    short_gaze_count = 0
    dt.set_index('gazenum')

    short_duration_indices = durations[durations.lt(min_delta)].index.values
    short_gaze_count = len(short_duration_indices)
    dt.loc[dt['gazenum'].isin(short_duration_indices), 'gaze'] = np.nan

    # for x in trange(durations.index.min(), durations.index.max()):
    # if durations.loc[x] < min_delta:
    # short_gaze_count += 1
    # dt['gaze'].where(dt['gazenum'] != x, inplace=True)
    # dt.loc[x,'gaze']  = np.nan
    # dt.loc[dt['gazenum'] == x, 'gaze'] = np.nan
    dt.reset_index()
    # print("{} transition gazes out of {} gazes total.".format(short_gaze_count, n))
    dt['gaze'].fillna(method='bfill', inplace=True)
    dt['gazenum'] = (dt['gaze'].shift(1) != dt['gaze']).astype(int).cumsum()
    # print("{} gazes after removing transitions.".format(dt['gazenum'].max()))

    drivedata.data = polars.from_pandas(dt)
    return drivedata

@registerFilter()
def mergeEvents(drivedata: pydre.core.DriveData, eventDirectory: str):

    # TODO: convert to use polars

    dt = drivedata.data.to_pandas()

    for drive, filename in zip(dt, drivedata.sourcefilename):
        event_filename = Path(eventDirectory) / Path(filename).with_suffix(".evt").name
        event_data = pandas.read_csv(event_filename, sep='\s+', na_values='.', header=0, skiprows=0, usecols=[0, 2, 4],
                                     names=['vidTime', 'simTime', 'Event_Name'])
        # find all keypress events:
        event_types = pandas.Series(event_data['Event_Name'].unique())
        event_types = event_types[event_types.str.startswith('KEY_EVENT')].to_list()
        if len(event_types) == 0:
            continue

        # add two columns, for the indexes corresponding to the start time and end time of the key events
        event_data_key_presses = event_data.loc[event_data['Event_Name'].isin(event_types)]
        event_data_key_presses['startIndex'] = drive['SimTime'].searchsorted(event_data_key_presses['simTime'])
        event_data_key_presses['stopIndex'] = drive['SimTime'].searchsorted(event_data_key_presses['simTime'] + 0.5)

        # make the new columns in the drive data
        for col in event_types:
            drive[col] = 0
        # merge the event data into the drive data
        for index, row in event_data_key_presses.iterrows():
            data_col_name = row['Event_Name']
            drive[data_col_name].loc[range(row['startIndex'], row['stopIndex'])] = 1

            # start_time and stopTime of key event f in speedbump2 are flipped. We might want to remove the if statement below if
            # this function is used for future studies
            if row['stopIndex'] < row['startIndex']:
                drive[data_col_name].loc[range(row['stopIndex'], row['startIndex'])] = 1

    drivedata.data = pl.from_pandas(dt)
    return drivedata


# copy F key presses to task fail column, added for speedbump 2 study 
def mergeFintoTaskFail(drivedata: pydre.core.DriveData):
    if 'KEY_EVENT_F' in drivedata.data.columns:
        drivedata.data = drivedata.data.select([
            pl.col("*").exclude("TaskFail"),
            (pl.col("TaskFail") + pl.col("KEY_EVENT_F")).cast("int").clip(0, 1)
        ])
    return drivedata


@registerFilter()
def speedLimitTransitionMarker(drivedata: pydre.core.DriveData, speedlimitcol: str):
    speedlimitpos = drivedata.data.select(
        [(pl.col(speedlimitcol).shift() != pl.col(speedlimitcol)).alias("SpeedLimitPositions"),
         speedlimitcol,
         "XPos",
         "DatTime"
        ]
    )

    block_marks = speedlimitpos.filter(pl.col("SpeedLimitPositions") == True)
    drivedata.data = drivedata.data.with_columns(
        pl.lit(None).cast(pl.Int32).alias("SpeedLimitBlocks")
    )

    mph2mps = 0.44704

    blocknumber = 1
    for row in block_marks.rows(named=True):
        drivedata.data = drivedata.data.with_columns(pl.when(pl.col("DatTime").cast(pl.Float32).is_between(row["DatTime"] - 5,
                                                                                        row["DatTime"] + 5)).
                                                 then(blocknumber).
                                                 otherwise(pl.col("SpeedLimitBlocks")).alias("SpeedLimitBlocks"))
        blocknumber += 1

    return drivedata

@registerFilter()
def numberTaskInstance(drivedata: pydre.core.DriveData):
    dt = pandas.DataFrame(drivedata.data)
    # dt.to_csv('dt.csv')
    dt['KEY_EVENT_PF'] = dt['KEY_EVENT_P'] + dt['TaskFail']
    diff = dt[['KEY_EVENT_T', 'KEY_EVENT_PF']].diff()
    startPoints = diff.loc[diff['KEY_EVENT_T'] == 1.0]  # all the points when T is pressed
    endPoints = diff.loc[diff['KEY_EVENT_PF'] == 1.0]  # all the points when P is pressed

    event = startPoints.append(endPoints)
    event = event.sort_index()
    event['drop_T'] = event['KEY_EVENT_T'].diff()
    event['drop_P'] = event['KEY_EVENT_PF'].diff()
    event.fillna(1)

    if event['KEY_EVENT_PF'].iloc[0] == 1:
        event = event.drop(event.index[0])

    time = []
    for t in event.index:
        time.append(dt.at[t, 'DatTime'])
    event['time'] = time
    event = event.loc[(event['drop_T'] != 0) & (event['drop_P'] != 0)]

    event.to_csv('event.csv')
    instance_index = 0
    ins = 1
    while (instance_index < len(event) - 1):
        begin = event.index[instance_index]
        end = event.index[instance_index + 1]
        dt.loc[begin:end, "TaskInstance"] = ins
        instance_index = instance_index + 2
        ins += 1
    drivedata.data = dt
    return drivedata

@registerFilter()
def writeToCSV(drivedata: pydre.core.DriveData, outputDirectory: str):
    filename = os.path.splitext(os.path.basename(drivedata.sourcefilename))
    output_path = os.path.join(outputDirectory, filename) + '.csv'
    drivedata.data.write_csv(output_path)

    return drivedata

@registerFilter()
def filetimeToDatetime(ft: int):
    EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as filetime
    HUNDREDS_OF_NS = 10000000
    s, ns100 = divmod(ft - EPOCH_AS_FILETIME, HUNDREDS_OF_NS)
    try:
        result = datetime.datetime.fromtimestamp(s, tz=datetime.timezone.utc).replace(microsecond=(ns100 // 10))
    except OSError:
        # happens when the input to fromtimestamp is outside of the legal range
        result = None
    return result

def mergeSplitFiletime(hi: int, lo: int):
    return struct.unpack('Q', struct.pack('LL', lo, hi))[0]

@registerFilter()
def smarteyeTimeSync(drivedata: pydre.core.DriveData, smarteye_vars: List[str]):

# TODO: switch to using polars

    dt = drivedata.data.to_pandas()
    # REALTIME_CLOCK is the 64-bit integer timestamp from SmartEye
    # The clock data from SimObserver is in two different 32-bit integer values:
    # hiFileTime encodes the high-order bits of the clock data
    # lowFileTime encodes the low-order bits of the clock data
    dt["SimCreatorClock"] = np.vectorize(mergeSplitFiletime)(
        dt['hiFileTime'], dt['lowFileTime'])
    dt["SimCreatorClock"] = dt['SimCreatorClock'].apply(filetimeToDatetime)
    dt["SmartEyeClock"] = np.vectorize(filetimeToDatetime)(dt['REALTIME_CLOCK'])

    # make a new data table with only the smarteye vars, for preparation for realignment
    # first we should check if all the varables we want to shift are actually in the data
    orig_columns = set(dt.columns)
    smarteye_columns = set(smarteye_vars)

    if not smarteye_columns.issubset(orig_columns):
        logger.error("Some columns defined in the filter parameters are not in the DriveData: {}"%[smarteye_columns-orig_columns])
        # there is probably a cleaner way to do this operation.
        # We want to keep only the smarteye data columns that are actually in the data file
        smarteye_columns = smarteye_columns - (smarteye_columns-orig_columns)

    smarteye_columns.add("SmartEyeClock")
    smarteye_data = dt[smarteye_columns]
    simcreator_data = dt[orig_columns-smarteye_columns]
    drivedata.data = pl.from_pandas(pandas.merge_asof(simcreator_data, smarteye_data,
                                                      left_on="SimCreatorClock", right_on="SmartEyeClock", ))
    return drivedata

