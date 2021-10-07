
from tqdm import tqdm, trange

import argparse
import glob
import pandas
import re
import numpy as np
import os, os.path

import pdb

from pandas.api.types import CategoricalDtype

datafile_re = re.compile("([^_]+)_Sub_(\d+)_Drive_(\d+)(?:.*).dat")

# ESTIMATED_CLOSEST_WORLD_INTERSECTION FILTERED_GAZE_OBJ_NAME

def smoothGazeData(dt, timeColName="VidTime", gazeColName="FILTERED_GAZE_OBJ_NAME"):
    cat_type = CategoricalDtype(categories=['None', 'localCS.dashPlane', 'localCS.WindScreen', 'onroad', 'offroad'])
    dt['gaze'] = dt[gazeColName].astype(cat_type)

    #dt['gaze'].replace(['None', 'car.dashPlane', 'car.WindScreen'], ['offroad', 'offroad', 'onroad'], inplace=True)
    dt['gaze'].replace(['None', 'localCS.dashPlane', 'localCS.WindScreen'], ['offroad', 'offroad', 'onroad'], inplace=True)

    if len(dt['gaze'].unique()) < 2:
        print("Bad gaze data, not enough variety. Aborting")
        return None

    # smooth frame blips
    gaze_same = (dt['gaze'].shift(-1) == dt['gaze'].shift(1)) & (dt['gaze'].shift(-2) == dt['gaze'].shift(2)) & (dt['gaze'].shift(-2) == dt['gaze'].shift(-1)) & (dt['gaze'] != dt['gaze'].shift(1))
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
            #dt['gaze'].where(dt['gazenum'] != x, inplace=True)
            #dt.loc[x,'gaze']  = np.nan
            dt.loc[dt['gazenum'] == x, 'gaze'] = np.nan
    dt.reset_index()
    print("{} transition gazes out of {} gazes total.".format(short_gaze_count, n))
    dt['gaze'].fillna(method='bfill', inplace=True)
    dt['gazenum'] = (dt['gaze'].shift(1) != dt['gaze']).astype(int).cumsum()
    print("{} gazes after removing transitions.".format(dt['gazenum'].max()))
    return dt

def numberSwitchBlocks(dt):
    #dt.set_index('timedelta', inplace=True)
    blocks = (dt != dt.shift()).TaskStatus.cumsum()
    blocks[dt.TaskStatus == 0] = None
    dt["taskblocks"] = blocks
    dt = dt.reset_index()
    return dt


def process_filelist(filelist, outpath, gazetype="FILTERED_GAZE_OBJ_NAME"):
    for fn in filelist:
        dt = pandas.read_csv(fn, sep='\s+', na_values='.')
        match = datafile_re.search(os.path.basename(fn))
        experiment_name, subject_id, drive_id = match.groups()
        print("processing " + fn)
        print("Experiment {}, Subject {}, drive {}".format(experiment_name, subject_id, drive_id))
        print("-- Smoothing gaze data")
        dt = smoothGazeData(dt, gazeColName=gazetype)
        if dt is None:
            continue
        print("-- Converting switch blocks")
        dt = numberSwitchBlocks(dt)
        newfilename = os.path.join(outpath, os.path.basename(fn))
        print("-- Writing out file " + newfilename)
        dt.to_csv(newfilename, sep=" ", na_rep='.', index=False, columns=["VidTime", "SimTime", "LonAccel",
                                                                          "LatAccel", "Throttle",
                 "Brake", "HeadwayTime", "RoadOffset", "XPos", "YPos", "ZPos", "TaskID",
                "TaskStatus", "TaskFail", "DriveID", "ParticipantID", "gaze", "gazenum", "taskblocks"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help=".dat files to process")
    parser.add_argument("--outdir", nargs=1, required=True,  help="directory to output processed files")
    parser.add_argument("--est", default=False, action='store_true', help="use estimate gaze based on head position")
    args = parser.parse_args()
    filelist = []
    outpath = os.path.abspath(args.outdir[0])
    if args.est:
        gazetype = "ESTIMATED_CLOSEST_WORLD_INTERSECTION"
    else:
        gazetype = "FILTERED_GAZE_OBJ_NAME"
    print(gazetype)
    if (not os.path.isdir(outpath)):
        print("Output directory does not exist" + outpath)
        exit()
    for g in args.files:
        filelist.extend(glob.glob(g))
    process_filelist(filelist, outpath, gazetype)

if __name__ == "__main__":
    main()
