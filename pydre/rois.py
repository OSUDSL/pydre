# -*- coding: utf-8 -*-

import pydre.core
import pandas as pd
import csv
import re
import logging
logger = logging.getLogger(__name__)


class TimeROI():

	def __init__(self, filename, nameprefix=""):
		# parse time filename values
		self.time_file = open(filename, "r")
		self.name_prefix = nameprefix

	def split(self, datalist):
		"""
		return list of pydre.core.DriveData objects
		the 'roi' field of the objects will be filled with the roi tag listed
		in the roi definition file column name
		"""
		table = list(csv.reader(self.time_file))
		titles = table[0]
		outputs = []
		for row in range(1, len(table)):
			subject = int(table[row][0])
			for roi in range(1, len(table[row])):
				data_frame = []
				drives = []
				source_files = []
				for drive_info in TimeROI.getCellInfo(table[row][roi]):
					# Add each drive specified by a particular cell data
					start_time, end_time, driveID = drive_info
					for item in datalist:
						# Find the proper subject and drive in the input data
						if (item.SubjectID == subject and  driveID in item.DriveID):
							data_frame.append(pydre.core.sliceByTime(start_time, end_time, "VidTime", item.data[0]))
							drives.append(item.DriveID)
							source_files.append(item.sourcefilename)
							break
				if len(drives) == 0:
					logger.warning("No data for ROI (subject: {}, roi: {})".format(subject, titles[roi]))
				else:
					outputs.append(pydre.core.DriveData(subject, drives, titles[roi], data_frame, source_files))
		return outputs

	def getCellInfo(cell_content):
		# FORMAT- 1:15:10-1:20:30#2 02:32-08:45#3
		# GROUPS 0 = start time, 1 = end time, 2 = driveID (1 if not specified)
		cell_regex = "(\d?:?\d?\d:\d\d)-(\d?:?\d?\d:\d\d)#?(\d+)?"
		# GROUPS: 0 = hour digit (if nec), 1 = minute digit, 2 = seconds digit
		time_regex = "(?:(\d):)?(\d\d|^\d):(\d\d)"
		cell_info = []
		for drive in cell_content.split():
			drive_info = re.match(cell_regex, drive)
			driveID = 1
			if drive_info.groups()[2] is not None:
				driveID = int(drive_info.groups()[2])

			start_info = re.match(time_regex, drive_info.groups()[0])
			end_info = re.match(time_regex, drive_info.groups()[1])
			start_hour = 0
			start_minute = 0
			start_second = 0
			if start_info.groups()[0] is not None:
				start_hour = int(start_info.groups()[0])

			if start_info.groups()[1] is not None:
				start_minute = int(start_info.groups()[1])

			if start_info.groups()[2] is not None:
				start_second = int(start_info.groups()[2])

			end_hour = 0
			end_minute = 0
			end_second = 0
			if end_info.groups()[0] is not None:
				end_hour = int(end_info.groups()[0])

			if end_info.groups()[1] is not None:
				end_minute = int(end_info.groups()[1])

			if end_info.groups()[2] is not None:
				end_second = int(end_info.groups()[2])

			start_VidTime = start_hour * 3600 + start_minute * 60 + start_second
			end_VidTime = end_hour * 3600 + end_minute * 60 + end_second

			cell_info.append([start_VidTime, end_VidTime, driveID])
		return cell_info
