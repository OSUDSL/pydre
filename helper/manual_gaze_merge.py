
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
        print("-- Converting switch blocks")
        dt = numberSwitchBlocks(dt)
        newfilename = os.path.join(outpath, os.path.basename(fn))
        print("-- Writing out file " + newfilename)
        dt.to_csv(newfilename, sep=" ", na_rep='.', index=False, columns=["VidTime", "SimTime", "LonAccel",
                                                                          "LatAccel", "Throttle",
                 "Brake", "HeadwayTime", "RoadOffset", "XPos", "YPos", "ZPos", "TaskID",
                "TaskStatus", "TaskFail", "DriveID", "ParticipantID", "gaze", "gazenum", "taskblocks"])

def merge_dat(dat_filename, gaze_filename):

    dt = pandas.read_csv(dat_filename, sep='\s+', na_values='.')
    gaze = pandas.read_csv(gaze_filename)    
    print("merging {} with {}".format(dat_filename, gaze_filename))

    aa = pandas.merge_asof(dt, gaze, left_on="VidTime", right_on="Time", direction='forward')
    aa['gaze'] = aa['Default']
    aa.gaze.fillna("onroad", inplace=True)
    aa.gaze.replace("GazeOff", "offroad", inplace=True)
    aa = numberSwitchBlocks(aa)
    aa['gazenum'] = (aa['gaze'].shift(1) != aa['gaze']).astype(int).cumsum()
    return aa

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dat", nargs=1, required=True,  help="input dat file")
    parser.add_argument("--gaze", nargs=1, required=True,  help="gaze file from Solomon Coder")
    parser.add_argument("--out", nargs=1, required=True,  help="output dat file")

    args = parser.parse_args()
    augmented_dat = merge_dat(args.dat[0], args.gaze[0])
    augmented_dat.to_csv(args.out[0], sep=" ", na_rep='.', index=False, columns=["VidTime", "SimTime", "LonAccel",
                "LatAccel", "Throttle",
                "Brake", "HeadwayTime", "RoadOffset", "XPos", "YPos", "ZPos", "TaskID",
                "TaskStatus", "TaskFail", "DriveID", "ParticipantID", "gaze", "gazenum", "taskblocks"])


if __name__ == "__main__":
    main()
