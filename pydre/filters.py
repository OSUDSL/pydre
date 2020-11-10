import pandas
from pandas import CategoricalDtype
from tqdm import tqdm, trange

import pandas
import pydre.core
import numpy as np
import logging


import ctypes

logger = logging.getLogger('PydreLogger')

# filters defined here take ____________ and return a ______________


def smoothGazeData(drivedata: pydre.core.DriveData, timeColName="VidTime", gazeColName="FILTERED_GAZE_OBJ_NAME"):
    for d in drivedata.data:
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
    print("{} frame blips".format(gaze_same.sum()))
    dt.loc[gaze_same, 'gaze'] = dt['gaze'].shift(-1)

    # adjust for 100ms latency
    dt['gaze'] = dt['gaze'].shift(-6)
    dt['timedelta'] = pandas.to_timedelta(dt[timeColName], unit="s")
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

    print("{} gazes before removing transitions".format(n))
    short_gaze_count = 0
    dt.set_index('gazenum')
    for x in trange(durations.index.min(), durations.index.max()):
        if durations.loc[x] < min_delta:
            short_gaze_count += 1
            # dt['gaze'].where(dt['gazenum'] != x, inplace=True)
            # dt.loc[x,'gaze']  = np.nan
            dt.loc[dt['gazenum'] == x, 'gaze'] = np.nan
    dt.reset_index()
    print("{} transition gazes out of {} gazes total.".format(short_gaze_count, n))
    dt['gaze'].fillna(method='bfill', inplace=True)
    dt['gazenum'] = (dt['gaze'].shift(1) != dt['gaze']).astype(int).cumsum()
    print("{} gazes after removing transitions.".format(dt['gazenum'].max()))
    return dt


filtersList = {}
filtersColNames = {}


def registerFilter(name, function, columnnames=None):
    filtersList[name] = function
    if columnnames:
        filtersColNames[name] = columnnames
    else:
        filtersColNames[name] = [name, ]


registerFilter('smoothGazeData', smoothGazeData)