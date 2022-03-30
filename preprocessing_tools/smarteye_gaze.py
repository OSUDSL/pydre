import argparse
import os
import sys
import glob
import numpy as np
import re
import pandas

from pandas.api.types import CategoricalDtype



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
    parser.add_argument("-f","--file", type= str, help="input dat file", required = True)
    parser.add_argument("-s","--start", type= float, help="start video timecode", required = True)
    parser.add_argument("-e","--end", type= float, help="end video timecode", required = True)
    args = parser.parse_args()
    print(file_list)
    results = runFiles(file_list)

    with open('tasks_out.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(("subject", "warning", "reactionTime", "startTime"))
        writer.writerows(results)


if __name__ == "__main__":
    main()