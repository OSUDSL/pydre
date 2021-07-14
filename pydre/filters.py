import pandas
from pandas import CategoricalDtype
from tqdm import tqdm, trange

import pandas
import pydre.core
import numpy as np
import logging

from pathlib import Path


import ctypes

logger = logging.getLogger('PydreLogger')

# filters defined here take a DriveData object and return an updated DriveData object

def numberSwitchBlocks(drivedata: pydre.core.DriveData,):
    required_col = ["TaskStatus"]
    diff = drivedata.checkColumns(required_col)
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()


    copy = pydre.core.DriveData.__init__(drivedata, drivedata.PartID, drivedata.DriveID, drivedata.roi,
                                         drivedata.data, drivedata.sourcefilename)

    for d in drivedata.data:
        dt = pandas.DataFrame(d)
        #dt.set_index('timedelta', inplace=True)
        blocks = ((dt != dt.shift()).TaskStatus.cumsum())/2
        blocks[dt.TaskStatus == 0] = None
        dt["taskblocks"] = blocks
        dt = dt.reset_index()
    return drivedata



def smoothGazeData(drivedata: pydre.core.DriveData, timeColName="DatTime", gazeColName="FILTERED_GAZE_OBJ_NAME"):
    required_col = [timeColName, gazeColName]
    diff = drivedata.checkColumns(required_col)
    if (len(diff) > 0):
        logger.error("\nCan't find needed columns {} in data file {} | function: {}".format(diff, drivedata.sourcefilename, pydre.core.funcName()))
        raise pydre.core.ColumnsMatchError()


    #copy = pydre.core.DriveData.__init__(drivedata, drivedata.PartID, drivedata.DriveID, drivedata.roi,
    #                                     drivedata.data, drivedata.sourcefilename)
    
    data = drivedata.data
    for d in data:
        dt = pandas.DataFrame(d)

        cat_type = CategoricalDtype(categories=['None', 'localCS.dashPlane', 'localCS.WindScreen', 'onroad', 'offroad'])
        dt['gaze'] = dt[gazeColName].astype(cat_type)

        # dt['gaze'].replace(['None', 'car.dashPlane', 'car.WindScreen'], ['offroad', 'offroad', 'onroad'], inplace=True)
        dt['gaze'].replace(['None', 'localCS.dashPlane', 'localCS.WindScreen'], ['offroad', 'offroad', 'onroad'],
                        inplace=True)

        if len(dt['gaze'].unique()) < 2:
            print("Bad gaze data, not enough variety. Aborting")
            return None

    # smooth frame blips
        gaze_same = (dt['gaze'].shift(-1) == dt['gaze'].shift(1)) & (dt['gaze'].shift(-2) == dt['gaze'].shift(2)) & (
                dt['gaze'].shift(-2) == dt['gaze'].shift(-1)) & (dt['gaze'] != dt['gaze'].shift(1))
        #print("{} frame blips".format(gaze_same.sum()))
        dt.loc[gaze_same, 'gaze'] = dt['gaze'].shift(-1)

    # adjust for 100ms latency
        dt['gaze'] = dt['gaze'].shift(-6)
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

        #print("{} gazes before removing transitions".format(n))
        short_gaze_count = 0
        dt.set_index('gazenum')
        
        
        durations.sort_values(ascending=True)

        index = 1
        while (durations.loc[index] < min_delta and index < durations.index.max()):
            # apply the code below to all rows < min_delta
            short_gaze_count += 1
            dt.loc[dt['gazenum'] == index, 'gaze'] = np.nan
            index += 1

        #for x in trange(durations.index.min(), durations.index.max()):
            #if durations.loc[x] < min_delta:
                #short_gaze_count += 1
                 # dt['gaze'].where(dt['gazenum'] != x, inplace=True)
                 # dt.loc[x,'gaze']  = np.nan
                #dt.loc[dt['gazenum'] == x, 'gaze'] = np.nan
        dt.reset_index()
        #print("{} transition gazes out of {} gazes total.".format(short_gaze_count, n))
        dt['gaze'].fillna(method='bfill', inplace=True)
        dt['gazenum'] = (dt['gaze'].shift(1) != dt['gaze']).astype(int).cumsum()
        #print("{} gazes after removing transitions.".format(dt['gazenum'].max()))
    return drivedata


def mergeEvents(drivedata: pydre.core.DriveData, eventDirectory: str):
    for drive, filename in zip(drivedata.data, drivedata.sourcefilename):
        event_filename = Path(eventDirectory) / Path(drivedata.sourcefilename).with_suffix(".evt").name
        event_data = pandas.read_csv(event_filename, sep='\s+', na_values='.', header=0, skiprows=0, usecols=[0, 2, 4], names=['startTime', 'stopTime', 'Event_Name'])
        # find all keypress events:
        event_types = pandas.Series(event_data['Event_Name'].unique())
        event_types = event_types[event_types.str.startswith('KEY_EVENT')].to_list()
        if len(event_types) == 0:
            continue

        # add two columns, for the indexes corresponding to the start time and end time of the key events
        event_data_key_presses = event_data.loc[event_data['Event_Name'].isin(event_types)]
        event_data_key_presses['startIndex'] = drive['DatTime'].searchsorted(event_data_key_presses['startTime'])
        event_data_key_presses['stopIndex'] = drive['DatTime'].searchsorted(event_data_key_presses['stopTime'])

        # make the new columns in the drive data
        for col in event_types:
            drive[col] = 0
        # merge the event data into the drive data
        for index, row in event_data_key_presses.iterrows():
            data_col_name = row['Event_Name']
            drive[data_col_name].loc[range(row['startIndex'], row['stopIndex'])] = 1

            # startTime and stopTime of key event f in speedbump2 are flipped. We might want to remove the if statement below if
            # this function is used for future studies
            if data_col_name == 'KEY_EVENT_F': 
                drive[data_col_name].loc[range(row['stopIndex'], row['startIndex'])] = 1

    return drivedata


# copy F key presses to task fail column, added for speedbump 2 study 
def mergeFintoTaskFail(drivedata: pydre.core.DriveData): 
    for d in drivedata.data:
        if 'KEY_EVENT_F' in d.columns:
            dt = pandas.DataFrame(d)
            merged = ((dt['TaskFail'] + dt['KEY_EVENT_F']).astype("int")).replace(2, 1)
            dt['TaskFail'] = merged
            d.to_csv('FtoF.csv')
    return drivedata



def numberTaskInstance(drivedata: pydre.core.DriveData):
    for d in drivedata.data:
        count = 0
        dt = pandas.DataFrame(d)
        #dt.loc[dt.DatTime < 1, "TaskInstance"] = 1
        diff = dt[['KEY_EVENT_T', 'KEY_EVENT_P']].diff()
        startPoints = diff.loc[diff['KEY_EVENT_T'] == 1.0]
        endPoints = diff.loc[diff['KEY_EVENT_P'] == 1.0]
        length = len(startPoints.index)
        instance_index = 1
        while (instance_index <= length):
            begin = startPoints.index[instance_index - 1]
            end = endPoints.index[instance_index - 1]
            dt.loc[begin:end, "TaskInstance"] = instance_index
            #print(begin)
            #print(end)
            #print(dt.loc[startPoints.index[instance_index - 1]:endPoints.index[instance_index - 1]])
            #print(d)
            instance_index = instance_index + 1
        drivedata.data[count] = dt
        count = count + 1
    drivedata.data[0].to_csv("Ins.csv")
    return drivedata


filtersList = {}
filtersColNames = {}


def registerFilter(name, function, columnnames=None):
    filtersList[name] = function
    if columnnames:
        filtersColNames[name] = columnnames
    else:
        filtersColNames[name] = [name, ]


registerFilter('smoothGazeData', smoothGazeData)
registerFilter('numberSwitchBlocks', numberSwitchBlocks)
registerFilter('mergeEvents', mergeEvents)
registerFilter('mergeFintoTaskFail', mergeFintoTaskFail)
registerFilter('numberTaskInstance', numberTaskInstance)