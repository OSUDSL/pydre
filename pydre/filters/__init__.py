from pandas import CategoricalDtype

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

@registerFilter()
def boxIdentificationTime(drivedata: pydre.core.DriveData, button_column="ResponseButton"):
    #check if required column names for mesopic study
    required_col = ["SimTime", "BoxStatus", button_column]
    diff = drivedata.checkColumns(required_col)
    df = pandas.DataFrame(drivedata.data)
    dt = pandas.DataFrame(df, columns=required_col)  # drop other columns
    dt = pandas.DataFrame.drop_duplicates(dt.dropna(axis=0, how='any'))  # remove nans and drop duplicates
    #Get DataFrame object and specific columns in data frame
    time = dt["SimTime"]
    boxStatus = dt["BoxStatus"]
    response = dt[button_column]
    #Subtract with previous row value to find the start times of each box
    boxStatus = boxStatus.diff(1)
    #Get the specific row indices of the start times for each box
    boxOnStart = boxStatus[boxStatus.values > 0.5].index[0:]
    #List to Hold the user reaction Time for indentifiying boxes
    reactionTime = list()
    #Iterate through the box start time indices
    for i in range(0, len(boxOnStart)):
        #Get the actual start time for when the box first starts appearing
        startTime = time.loc[boxOnStart[i]]
        #Find when user (if any) pressed response
        if i == len(boxOnStart) - 1:
            detected = response.loc[boxOnStart[i]:].diff(1)
        else:
            detected = response.loc[boxOnStart[i]:boxOnStart[i+1]].diff(1)
        #Get the detected indexes of when user (if any) pressed response button for the specific box
        detectedIndices = detected[detected.values > 0.5].index[0:]
        #if no response then append negative result 
        if len(detectedIndices) == 0:
            reactionTime.append(-1)
        else:
            pressTime = time.loc[detectedIndices[0]]
            #Append the reaction time from subtracting start time from when user presses response button first 
            reactionTime.append(pressTime - startTime)
    #Concat to data frame
    reactionTimeFrame = pandas.DataFrame({'ReactionTime': reactionTime})
    dt = pandas.concat([dt, reactionTimeFrame], ignore_index=True)
    #update drivedata data 
    drivedata.data["ReactionTime"] = dt["ReactionTime"]
    #return drivedata object
    return drivedata

@registerFilter()
def numberBoxBlocks(drivedata: pydre.core.DriveData, box_column="BoxStatus"):
    required_col = [box_column]
    diff = drivedata.checkColumns(required_col)
    dt = drivedata.data
    blocks = ((dt != dt.shift())[box_column].cumsum()) / 2
    blocks[dt[box_column] == 0] = None
    # add about 5 seconds after the box disappears
    blocks.fillna(method="ffill", inplace=True, limit=5*60)
    dt["boxBlocks"] = blocks
    dt = dt.reset_index()
    drivedata.data = dt
    return drivedata

@registerFilter()
def numberFollowingCarBrakes(drivedata: pydre.core.DriveData, box_column="FollowCarBrakingStatus"):
    required_col = [box_column]
    diff = drivedata.checkColumns(required_col)
    dt = drivedata.data
    brakes = ((dt != dt.shift())[box_column].cumsum()) / 2
    brakes[dt[box_column] == 0] = None
    dt["carBlocks"] = brakes
    dt = dt.reset_index()
    drivedata.data = dt
    return drivedata

@registerFilter()
def numberEventBlocks(drivedata: pydre.core.DriveData, box_column="CriticalEventStatus"):
    required_col = [box_column]
    diff = drivedata.checkColumns(required_col)
    dt = drivedata.data
    eventBlocks = ((dt != dt.shift())[box_column].cumsum()) / 2
    eventBlocks[dt[box_column] == 0] = None
    # add about 2 seconds after the event occurs
    #eventBlocks.fillna(method="ffill", inplace=True, limit=2*60)
    dt["eventBlocks"] = eventBlocks
    dt = dt.reset_index()
    drivedata.data = dt
    return drivedata


@registerFilter()
def numberSwitchBlocks(drivedata: pydre.core.DriveData, ):
    required_col = ["TaskStatus"]
    diff = drivedata.checkColumns(required_col)

    dt = pandas.DataFrame(drivedata.data)
    blocks = ((dt != dt.shift()).TaskStatus.cumsum()) / 2
    blocks[dt.TaskStatus == 0] = None
    dt["taskblocks"] = blocks
    dt = dt.reset_index()
    drivedata.data = dt
    return drivedata

@registerFilter()
def smoothGazeData(drivedata: pydre.core.DriveData, timeColName: str = "DatTime",
                   gazeColName: str = "FILTERED_GAZE_OBJ_NAME", latencyShift=6):
    required_col = [timeColName, gazeColName]
    diff = drivedata.checkColumns(required_col)

    dt = pandas.DataFrame(drivedata.data)
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
    drivedata.data = dt
    return drivedata

@registerFilter()
def mergeEvents(drivedata: pydre.core.DriveData, eventDirectory: str):
    for drive, filename in zip(drivedata.data, drivedata.sourcefilename):
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

    return drivedata


# copy F key presses to task fail column, added for speedbump 2 study 
def mergeFintoTaskFail(drivedata: pydre.core.DriveData):
    if 'KEY_EVENT_F' in drivedata.data.columns:
        dt = pandas.DataFrame(drivedata.data)
        merged = ((dt['TaskFail'] + dt['KEY_EVENT_F']).astype("int")).replace(2, 1)
        dt['TaskFail'] = merged
        drivedata.data = dt
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
    for data, sourcefile in zip(drivedata.data, drivedata.sourcefilename):
        filename = os.path.splitext(os.path.basename(sourcefile))[0]
        output_path = os.path.join(outputDirectory, filename) + '.csv'
        data.to_csv(output_path, index=False)
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
    # REALTIME_CLOCK is the 64-bit integer timestamp from SmartEye
    # The clock data from SimObserver is in two different 32-bit integer values:
    # hiFileTime encodes the high-order bits of the clock data
    # lowFileTime encodes the low-order bits of the clock data
    drivedata.data["SimCreatorClock"] = np.vectorize(mergeSplitFiletime)(
        drivedata.data['hiFileTime'], drivedata.data['lowFileTime'])
    drivedata.data["SimCreatorClock"] = drivedata.data['SimCreatorClock'].apply(filetimeToDatetime)
    drivedata.data["SmartEyeClock"] = np.vectorize(filetimeToDatetime)(drivedata.data['REALTIME_CLOCK'])

    # make a new data table with only the smarteye vars, for preparation for realignment
    # first we should check if all the varables we want to shift are actually in the data
    orig_columns = set(drivedata.data.columns)
    smarteye_columns = set(smarteye_vars)

    if not smarteye_columns.issubset(orig_columns):
        logger.error("Some columns defined in the filter parameters are not in the DriveData: {}"%[smarteye_columns-orig_columns])
        # there is probably a cleaner way to do this operation.
        # We want to keep only the smarteye data columns that are actually in the data file
        smarteye_columns = smarteye_columns - (smarteye_columns-orig_columns)

    smarteye_columns.add("SmartEyeClock")
    smarteye_data = drivedata.data[smarteye_columns]
    simcreator_data = drivedata.data[orig_columns-smarteye_columns]
    drivedata.data = pandas.merge_asof(simcreator_data, smarteye_data, left_on="SimCreatorClock", right_on="SmartEyeClock", )

    return drivedata

