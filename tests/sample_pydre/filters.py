import pandas
from pandas import CategoricalDtype
from tqdm import tqdm, trange

import pandas
import tests.sample_pydre.core
import numpy as np
import logging


import ctypes

logger = logging.getLogger("PydreLogger")

# filters defined here take a DriveData object and return an updated DriveData object


def numberSwitchBlocks(
    drivedata: tests.sample_pydre.core.DriveData,
):
    copy = tests.sample_pydre.core.DriveData.__init__(
        drivedata,
        drivedata.PartID,
        drivedata.DriveID,
        drivedata.roi,
        drivedata.data,
        drivedata.sourcefilename,
    )

    for d in drivedata.data:
        dt = pandas.DataFrame(d)
        # dt.set_index('timedelta', inplace=True)
        blocks = ((dt != dt.shift()).TaskStatus.cumsum()) / 2
        blocks[dt.TaskStatus == 0] = None
        dt["taskblocks"] = blocks
        dt = dt.reset_index()
    return drivedata


def smoothGazeData(
    drivedata: tests.sample_pydre.core.DriveData,
    timeColName: str = "DatTime",
    gazeColName: str = "FILTERED_GAZE_OBJ_NAME",
    latencyShift=6,
):
    required_col = [timeColName, gazeColName]

    dt = pandas.DataFrame(drivedata.data)
    cat_type = CategoricalDtype(
        categories=[
            "None",
            "localCS.dashPlane",
            "localCS.WindScreen",
            "localCS.CSLowScreen",
            "onroad",
            "offroad",
        ]
    )
    dt["gaze"] = dt[gazeColName].astype(cat_type)

    # dt['gaze'].replace(['None', 'car.dashPlane', 'car.WindScreen'], ['offroad', 'offroad', 'onroad'], inplace=True)
    dt["gaze"].replace(
        ["None", "localCS.dashPlane", "localCS.WindScreen", "localCS.CSLowScreen"],
        ["offroad", "offroad", "onroad", "offroad"],
        inplace=True,
    )

    if len(dt["gaze"].unique()) < 2:
        print("Bad gaze data, not enough variety. Aborting")
        return None

    # smooth frame blips
    gaze_same = (
        (dt["gaze"].shift(-1) == dt["gaze"].shift(1))
        & (dt["gaze"].shift(-2) == dt["gaze"].shift(2))
        & (dt["gaze"].shift(-2) == dt["gaze"].shift(-1))
        & (dt["gaze"] != dt["gaze"].shift(1))
    )
    # print("{} frame blips".format(gaze_same.sum()))
    dt.loc[gaze_same, "gaze"] = dt["gaze"].shift(-1)

    # adjust for 100ms latency
    dt["gaze"] = dt["gaze"].shift(-latencyShift)
    dt["timedelta"] = pandas.to_timedelta(dt[timeColName].astype(float), unit="s")
    dt.set_index("timedelta", inplace=True)

    # filter out noise from the gaze column
    # SAE J2396 defines fixations as at least 0.2 seconds,
    min_delta = pandas.to_timedelta(0.2, unit="s")
    # so we ignore changes in gaze that are less than that

    # find list of runs
    dt["gazenum"] = (dt["gaze"].shift(1) != dt["gaze"]).astype(int).cumsum()
    n = dt["gazenum"].max()
    dt = dt.reset_index()
    # breakpoint()
    durations = (
        dt.groupby("gazenum")["timedelta"].max()
        - dt.groupby("gazenum")["timedelta"].min()
    )

    # print("{} gazes before removing transitions".format(n))
    short_gaze_count = 0
    dt.set_index("gazenum")

    short_duration_indices = durations[durations.lt(min_delta)].index.values
    short_gaze_count = len(short_duration_indices)
    dt.loc[dt["gazenum"].isin(short_duration_indices), "gaze"] = np.nan

    # for x in trange(durations.index.min(), durations.index.max()):
    # if durations.loc[x] < min_delta:
    # short_gaze_count += 1
    # dt['gaze'].where(dt['gazenum'] != x, inplace=True)
    # dt.loc[x,'gaze']  = np.nan
    # dt.loc[dt['gazenum'] == x, 'gaze'] = np.nan
    dt.reset_index()
    # print("{} transition gazes out of {} gazes total.".format(short_gaze_count, n))
    dt["gaze"].fillna(method="bfill", inplace=True)
    dt["gazenum"] = (dt["gaze"].shift(1) != dt["gaze"]).astype(int).cumsum()
    # print("{} gazes after removing transitions.".format(dt['gazenum'].max()))
    drivedata.data = dt
    return drivedata


def mergeEvents(drivedata: tests.sample_pydre.core.DriveData, eventDirectory: str):
    for drive, filename in zip(drivedata.data, drivedata.sourcefilename):
        event_filename = Path(eventDirectory) / Path(filename).with_suffix(".evt").name
        event_data = pandas.read_csv(
            event_filename,
            sep="\s+",
            na_values=".",
            header=0,
            skiprows=0,
            usecols=[0, 2, 4],
            names=["vidTime", "simTime", "Event_Name"],
        )
        # find all keypress events:
        event_types = pandas.Series(event_data["Event_Name"].unique())
        event_types = event_types[event_types.str.startswith("KEY_EVENT")].to_list()
        if len(event_types) == 0:
            continue

        # add two columns, for the indexes corresponding to the start time and end time of the key events
        event_data_key_presses = event_data.loc[
            event_data["Event_Name"].isin(event_types)
        ]
        event_data_key_presses["startIndex"] = drive["SimTime"].searchsorted(
            event_data_key_presses["simTime"]
        )
        event_data_key_presses["stopIndex"] = drive["SimTime"].searchsorted(
            event_data_key_presses["simTime"] + 0.5
        )

        # make the new columns in the drive data
        for col in event_types:
            drive[col] = 0
        # merge the event data into the drive data
        for index, row in event_data_key_presses.iterrows():
            data_col_name = row["Event_Name"]
            drive[data_col_name].loc[range(row["startIndex"], row["stopIndex"])] = 1

            # start_time and stopTime of key event f in speedbump2 are flipped. We might want to remove the if statement below if
            # this function is used for future studies
            if row["stopIndex"] < row["startIndex"]:
                drive[data_col_name].loc[range(row["stopIndex"], row["startIndex"])] = 1

    return drivedata


filtersList = {}
filtersColNames = {}


def registerFilter(name, function, columnnames=None):
    filtersList[name] = function
    if columnnames:
        filtersColNames[name] = columnnames
    else:
        filtersColNames[name] = [
            name,
        ]


registerFilter("smoothGazeData", smoothGazeData)
registerFilter("numberSwitchBlocks", numberSwitchBlocks)
