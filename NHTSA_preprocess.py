


import argparse
import glob
import pandas
import re
import numpy as np
import os, os.path

datafile_re = re.compile("([^_]+)_Sub_(\d+)_Drive_(\d+)(?:.*).dat")


def process_filelist(filelist, outpath):
    for fn in filelist:
        dt = pandas.read_csv(fn, sep=" ", na_values='.')
        match = datafile_re.search(fn)
        experiment_name, subject_id, drive_id = match.groups()
        print("processing " + fn)
        print("Experiment {}, Subject {}, drive {}".format(experiment_name, subject_id, drive_id))
        print("-- Smoothing gaze data")
        dt = smoothGazeData(dt)
        print("-- Converting switch blocks")
        dt = numberSwitchBlocks(dt)
        newfilename = os.path.join(outpath, os.path.basename(fn))
        print("-- Writing out file " + newfilename)
        dt.to_csv(newfilename, sep="\t")

def test_process(fn):
    dt = pandas.read_csv(fn, sep=" ", na_values='.')
    return process(dt)

def summarizeGazeBlock(block, timeColName="VidTime", gazeColName="ESTIMATED_CLOSEST_WORLD_INTERSECTION"):
    # find the gaze sequence in block, which has a vidTime column and a gaze column
    block = pandas.DataFrame(block, columns=([timeColName, gazeColName]))
    cat_type = CategoricalDtype(categories=['None', 'car.dashPlane', 'car.WindScreen'])
    block[gazeColName] = block[gazeColName].astype(cat_type)
    block[timeColName] = pandas.to_timedelta(block[timeColName], unit="s")
    block.set_index(timeColName, inplace=True)

    # filter out noise from the gaze column
    # SAE J2396 defines fixations as at least 0.2 seconds,
    min_delta = pandas.to_timedelta(0.2, unit='s')
    # so we ignore changes in gaze that are less than that

    # find list of runs
    block['gazenum'] = (block[gazeColName].shift(1) != block[gazeColName]).astype(int).cumsum()
    durations = block.reset_index().groupby('gazenum').max() - block.reset_index().groupby('gazenum').min()
    n = block['gazenum'].max()
    block = block.reset_index()

    for x in range(n):
        if durations.iloc[x][timeColName] < min_delta:
            block.loc[block['gazenum'] == x, gazeColName] = np.nan

    block.fillna(method='bfill', inplace=True)
    return block

def process(dt):
    dt = dt[dt.TaskStatus.notnull()]

    blocks = (dt != dt.shift()).TaskStatus.cumsum()
    blocks[dt.TaskStatus == 0] = 0
    dt["blocks"] = blocks
    taskStatusBlocks = dt.groupby("blocks")
    taskIDs = taskStatusBlocks.apply(lambda x: np.unique(x.TaskID))
    taskfails = taskStatusBlocks.apply(lambda x: np.max(x.TaskFail))
    taskstart = taskStatusBlocks.apply(lambda x: np.min(x.VidTime))
    taskend = taskStatusBlocks.apply(lambda x: np.max(x.VidTime))
    taskDuration = taskend - taskstart
    res = pandas.DataFrame(data={'taskID': taskIDs,
        'taskFail': taskfails, 'taskStart': taskstart,
        'taskDuration': taskDuration, 'taskEnd': taskend})
    return res[res.index!=0]

def convert_filelist(filelist):
    for fn in filelist:
        prefix, ext = os.path.splitext(fn)
        newfn = prefix + ".csv"
        dt = pandas.read_csv(fn, sep=" ", na_values='.')
        print(fn, " -> ", newfn)
        dt.to_csv(newfn, index=False)

def runFiles(files):
    total_results = []
    for filename in files:
        d = pandas.read_csv(filename, sep='\s+', na_values='.')
        datafile_re = re.compile("([^_]+)_Sub_(\d+)_Drive_(\d+)(?:.*).dat")
        match = datafile_re.search(filename)
        experiment_name, subject_id, drive_id = match.groups()
        print("Running subject {}, drive {}".format(subject_id, drive_id))
        results = ecoCar(d)
        print("Got {} results.".format(len(results)))
        for (startTime, warning, rtTime) in results:
            total_results.append((subject_id, warning, rtTime, startTime))
    return total_results



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help=".dat files to process")
    parser.add_argument("--outdir", nargs=1, required=True,  help="directory to output processed files")
    args = parser.parse_args()
    filelist = []
    outpath = os.path.abspath(args.outdir)
    if (os.path.isdir(outpath))
    for g in args.files:
        filelist.extend(glob.glob(g))
    process_filelist(filelist, outpath)

if __name__ == "__main__":
    main()
