import sys
import os
import math
import glob
import pandas as pd
import re
import logging
import shutil

logger = logging.getLogger(__name__)

regular_expressions = ['(?:.*\\\)?(.*)_Sub_(\d+)_Drive_\d+\.dat', '(?:.*\\\)?([^_]+)_([^_]+)_([^_]+)_(\d+).dat']
regular_expressions_glob = ['*_Sub_*_Drive_*.dat', '*_*_*_*.dat']
regular_expressions_group = ['.*_Sub_(\d+)_Drive_(\d+)\.dat', '.*_(.*)_(.*)_(\d+)\.dat']
# 0 - SimObserver3 data file format
# 1 - SimCreator DX data file format

class MergeTool():

    # Creates a dict with an entry for each subject.
    # The value of each entry in the dict is a list of
    # drives in the order that they are to be merged.
    # Currently just orders by driveID from lowest to highest
    def groupBySubject(self, file_list, exp_index):
        global regular_expressions_group
        groups = {}
        name_pattern = re.compile(str(regular_expressions_group[exp_index]))
        for file_name in file_list:
            match = name_pattern.match(file_name)
            if (match):
                subject = match.group(1)
                drive = match.group(2)
                if exp_index == 2:
                    drive = match.group(3)
                if (subject in groups):
                    drive_group = groups[subject]
                    i = 0
                    while i < len(drive_group):
                        other_drive = name_pattern.match(drive_group[i]).group(2)
                        if (drive > other_drive):
                            i = i + 1
                        else:
                            break
                    drive_group.insert(i, file_name)
                else:
                    groups[subject] = [file_name]
        return groups

    def sequential_merge(self, input_directory, exp_index):
        global regular_expressions
        global regular_expressions_glob
        out_dir = os.makedirs(os.path.join(input_directory, 'MergedData'), exist_ok=True)
        out_dir_name = os.path.join(input_directory, 'MergedData')
        file_list = sorted(glob.glob(input_directory + '/' + regular_expressions_glob[exp_index]))
        subject_groups = self.groupBySubject(file_list, exp_index)
        warning = True
        for key in subject_groups:
            warning = False
            logger.info("merging for subject: ", key)
            drive_group = subject_groups[key]
            drive_group.sort()
            out_frame = pd.read_csv(drive_group[0], sep=' ', na_values='.', engine="c")
            name_pattern = re.compile(regular_expressions[exp_index])
            

            out_name = ""
            if exp_index == 0:
                match = name_pattern.match(drive_group[0])
                study = match.group(1)
                subject = match.group(2)
                out_name = study + "_Sub_" + subject + "_Drive_0.dat"
            elif exp_index == 1:
                match = name_pattern.match(drive_group[0])
                model = match.group(1)
                part_id = match.group(2)
                scen_name = match.group(3)
                unique_id = match.group(4)
                out_name = model + "_" + part_id + "_" + scen_name + "_" + str(int(unique_id)+1) + ".dat"
            
            source_dir = drive_group[0]
            out_frame['SourceId'] = source_dir[max(source_dir.find('\\'), source_dir.find('/')):]
            for drive in drive_group[1:]:
                # The latest out_frame's final SimTime. To be added across next_frame's SimTime column as a constant.
                # '-1' indices didn't work here, threw a pandas error. But this code produces desired result.
                timejump = out_frame[:]["SimTime"]
                timejumpdat = out_frame[:]["DatTime"]
                timeconstant = timejump[len(timejump) - 1]

                timejumpdat = out_frame[:]["DatTime"]
                timeconstantdat = timejumpdat[len(timejumpdat) - 1]

                next_frame = pd.read_csv(drive, sep=' ', na_values='.', engine="c")
                next_frame["SimTime"] += timeconstant
                next_frame["DatTime"] += timeconstantdat
                source_dir = drive
                next_frame['SourceId'] = source_dir[max(source_dir.find('\\'), source_dir.find('/')):]
                out_frame = out_frame.append(next_frame, ignore_index=True)
            out_frame.to_csv(os.path.join(out_dir_name, out_name),
                             sep=' ', na_rep=".", index=False)

        if warning is True:
            logger.warning("No files processed, check merge directory (-d) to ensure there are valid data files present.")

    def spatial_merge(self, input_directory, exp_index):
        global regular_expressions
        os.makedirs(os.path.join(input_directory, 'MergedData'), exist_ok=True)
        out_dir_name = os.path.join(input_directory, 'MergedData')
        file_list = glob.glob(input_directory + '/' + regular_expressions_glob[exp_index])

        subject_groups = self.groupBySubject(file_list, exp_index)
        for key in subject_groups:
            drive_group = subject_groups[key]
            out_frame = pd.read_csv(drive_group[0], sep=' ', na_values='.')
            if (len(drive_group) > 1):

                i = 0
                while i < len(drive_group):

                    i = i + 1
                    last_line = out_frame.tail(1)
                    last_x = last_line.XPos.iloc[0]
                    last_y = last_line.YPos.iloc[0]
                    last_time = last_line.SimTime.iloc[0]
                    next_frame = pd.read_csv(drive_group[i], sep=' ', na_values='.')
                    min_dist = float('inf')
                    min_index = 0

                    for index, row in next_frame.iterrows():
                        dist = (row.XPos - last_x) ** 2 + (row.YPos - last_y) ** 2

                        if (dist < min_dist):
                            min_index = index
                            min_dist = dist

                    start_time = next_frame.iloc[min_index].SimTime
                    next_frame = next_frame[min_index:]
                    next_frame["SimTime"] += last_time
                    out_frame = out_frame.append(next_frame, ignore_index=True)

                    if i + 1 >= len(drive_group):
                        break

                name_pattern = re.compile(regular_expressions[exp_index])
                match = name_pattern.match(drive_group[0])
                study = match.group(1)
                subject = match.group(2)

                out_name = ""
                if exp_index == 0:
                    match = name_pattern.match(drive_group[0])
                    study = match.group(1)
                    subject = match.group(2)
                    out_name = study + "_Sub_" + subject + "_Drive_0.dat"
                elif exp_index == 1:
                    match = name_pattern.match(drive_group[0])
                    model = match.group(1)
                    part_id = match.group(2)
                    scen_name = match.group(3)
                    #unique_id = match.group(4)
                    out_name = model + "_" + part_id + "_" + scen_name + "_" + str(int(unique_id)+1) + ".dat"

                out_frame.to_csv(os.path.join(out_dir_name, out_name), sep=' ')

            else:
                name_pattern = re.compile(regular_exp)
                match = name_pattern.match(drive_group[0])
                base_filename = match.group(1)
                out_frame.to_csv(os.path.join(out_dir_name, base_filename), sep=' ')

    def __init__(self, input_directory, merge_type="spatial", regular_expression_index=0):
        global regular_expressions
        logger.warning(regular_expressions[regular_expression_index])
        upper_type = merge_type.upper()
        if upper_type == "SPATIAL":
            self.spatial_merge(input_directory, regular_expression_index)
        elif upper_type == "SEQUENTIAL":
            self.sequential_merge(input_directory, regular_expression_index)
        else:
            raise ValueError(
                "Merge type \"{}\" not supported. Valid merge types: \"Spatial\" or \"Sequential\"".format(merge_type))
