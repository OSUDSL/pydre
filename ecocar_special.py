import csv
import argparse
import os
import sys
import glob
import re
import pandas

sys.path.append(os.path.join(os.path.dirname(__file__)))

import pydre

def ecoCar(d: pandas.DataFrame):
    event = 0
    reactionTimeList = list()
    df = pandas.DataFrame(d, columns=("SimTime", "WarningToggle", "FailureCode", "Throttle", "Brake", "Steer",
                                      "AutonomousDriving"))  # drop other columns
    df = pandas.DataFrame.drop_duplicates(df.dropna(axis=[0, 1], how='any'))  # remove nans and drop duplicates

    if (len(df) == 0):
        return reactionTimeList

    toggleOndf = df['WarningToggle'].diff(1)
    indicesToggleOn = toggleOndf[toggleOndf.values > .5].index[0:]
    indicesToggleOff = toggleOndf[toggleOndf.values < 0.0].index[0:]

    print("{} toggles found.".format(len(indicesToggleOn)))

    for counter in range(0, len(indicesToggleOn)):
        warningOn = int(indicesToggleOn[counter])
        warning = int(df["FailureCode"].loc[warningOn])
        startWarning = df["SimTime"].loc[warningOn]

        ## End time (start of warning time plus 15 seconds)

        warningPlus15 = df[(df.SimTime >= startWarning) & (df.SimTime <= startWarning + 15)]
        interactionList = list()

        thresholdBrake = 2
        initial_Brake = warningPlus15["Brake"].iloc[0]
        brakeVector = warningPlus15[ warningPlus15["Brake"] >= (initial_Brake + thresholdBrake)]
        if (len(brakeVector) > 0):
            interactionList.append(brakeVector["SimTime"].iloc[0]-startWarning)

        thresholdSteer = 2
        initial_Steer = warningPlus15["Steer"].iloc[0]
        steerVector = warningPlus15[ warningPlus15["Steer"] >= (initial_Steer + thresholdSteer)]
        if (len(steerVector) > 0):
            interactionList.append(steerVector["SimTime"].iloc[0]-startWarning)

        thresholdThrottle = 2
        initial_Throttle = warningPlus15["Throttle"].iloc[0]
        ThrottleVector = warningPlus15[ warningPlus15["Throttle"] >= (initial_Throttle + thresholdThrottle)]
        if (len(ThrottleVector) > 0):
            interactionList.append(ThrottleVector["SimTime"].iloc[0]-startWarning)

        AutonomousVector = warningPlus15[ warningPlus15["AutonomousDriving"] == 1]
        if (len(AutonomousVector) > 0):
            interactionList.append(AutonomousVector["SimTime"].iloc[0]-startWarning)

        interactionList = [x for x in interactionList if x > 0]
        # Compare all Reaction Times
        if (len(interactionList) != 0):
            print(startWarning, warning, min(interactionList))
            reactionTimeList.append((startWarning, warning, min(interactionList)))

    return reactionTimeList

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
    parser.add_argument("-d","--directory", type= str, help="the directory of files to process", required = True)
    args = parser.parse_args()
    file_list = glob.glob(args.directory + '/*_Sub_*_Drive_*.dat')
    results = runFiles(file_list)
    with open('ecocar_out.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(("subject", "warning", "reactionTime", "startTime"))
        writer.writerows(results)


if __name__ == "__main__":
    main()