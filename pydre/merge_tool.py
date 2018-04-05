import sys
import os
import math
import glob
import pandas as pd
import re
import shutil

class MergeTool():

	#Creates a dict with an entry for each subject. 
	#The value of each entry in the dict is a list of 
	#drives in the order that they are to be merged.
	#Currently just orders by driveID from lowest to highest
	def groupBySubject(self, file_list):
		groups = {}
		name_pattern = re.compile(".*_Sub_(\d+)_Drive_(\d+)\.dat")
		for file_name in file_list:
			match = name_pattern.match(file_name)
			if (match):
				subject = match.group(1)
				drive = match.group(2)
				if(subject in groups):
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

	def sequential_merge(self, input_directory):
		out_dir = os.makedirs(os.path.join(input_directory, 'MergedData'), exist_ok=True)
		out_dir_name = os.path.join(input_directory, 'MergedData')
		file_list = glob.glob(input_directory + '/*_Sub_*_Drive_*.dat')
		subject_groups = self.groupBySubject(file_list)

		for key in subject_groups:
			print("merging for subject: ", key)
			drive_group = subject_groups[key]
			out_frame = pd.read_csv(drive_group[0], sep='\s+', na_values='.', engine="c")
			name_pattern = re.compile("(?:.*\\\)?(.*)_Sub_(\d+)_Drive_\d+\.dat")
			match = name_pattern.match(drive_group[0])
			study = match.group(1)
			subject = match.group(2)
			for drive in drive_group[1:]:
				timejump = out_frame[:-1]["SimTime"]
				next_frame = pd.read_csv(drive, sep='\s+', na_values='.', engine="c")
				next_frame["SimTime"] += timejump
				out_frame = out_frame.append(next_frame)
			out_frame.to_csv(out_dir_name + "\\" + study + "_Sub_" + subject + "_Drive_0.dat", sep=' ', na_rep=".", index=False)

	def spatial_merge(self, input_directory):
		out_dir = os.makedirs(os.path.join(input_directory, 'MergedData'), exist_ok=True)
		out_dir_name = os.path.join(input_directory, 'MergedData')
		file_list = glob.glob(input_directory + '/*_Sub_*_Drive_*.dat')

		subject_groups = self.groupBySubject(file_list)

		for key in subject_groups:
			drive_group = subject_groups[key]
			out_frame = pd.read_csv(drive_group[0], sep='\s+', na_values='.')
			if (len(drive_group) > 1):
				i = 0
				while i < len(drive_group):
					i = i + 1
					last_line = out_frame.tail(1)
					last_x = last_line.XPos.iloc[0]
					last_y = last_line.YPos.iloc[0]
					last_time = last_line.SimTime.iloc[0]
					next_frame = pd.read_csv(drive_group[i], sep='\s+', na_values='.')
					min_dist = float('inf')
					min_index = 0
					for index, row in next_frame.iterrows():
						dist = (row.XPos - last_x) ** 2 + (row.YPos - last_y) ** 2
						if (dist < min_dist):
							min_index = index
							min_dist = dist
					start_time = next_frame.iloc[min_index].SimTime
					next_frame = next_frame[min_index:]
					next_frame.SimTime += last_time - start_time
					out_frame = out_frame.append(next_frame)

					if i + 1 >= len(drive_group):
						break
				name_pattern = re.compile("(?:.*\\\)?(.*)_Sub_(\d+)_Drive_\d+\.dat")
				match = name_pattern.match(drive_group[0])
				study = match.group(1)
				subject = match.group(2)
				out_frame.to_csv(out_dir_name + "\\" + study + "_Sub_" + subject + "_Drive_0.dat", sep=' ')
			else:
				name_pattern = re.compile("(?:.*\\\)?(.*_Sub_\d+_Drive_\d+\.dat)")
				match = name_pattern.match(drive_group[0])
				base_filename = match.group(1)
				out_frame.to_csv(out_dir_name + "\\" + base_filename, sep=' ')

	def __init__(self, input_directory, merge_type="spatial"):
		if merge_type == "spatial":
			self.spatial_merge(input_directory)
		elif merge_type == "sequential":
			self.sequential_merge(input_directory)
		else:
			raise ValueError("Merge type \"{}\" not supported.".format(merge_type))
