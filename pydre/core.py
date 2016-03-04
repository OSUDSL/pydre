# -*- coding: utf-8 -*-

import pandas
import logging
logger = logging.getLogger(__name__)


def sliceByTime(begin: float, end: float, column: str, drive_data: pandas.DataFrame):
	"""
		args:
			begin: float defnining the start point of the slice
			end: float defining the end part of the slice
			column: which column in the drive_data frame to use for the time.  This is usually SimTime or VidTime.
			drive_data: pandas DataFrame containing the data to be sliced

		returns:
			pandas.DataFrame slice containing requested time slice

	Given a start and end and a column name that represents a time value, output the slice that contains
	only the specified data.
	"""
	return(drive_data[(drive_data[column] >= begin) & (drive_data[column] <= end)])


class DriveData:

	def __init__(self, SubjectID: int, DriveID,	roi: str, data,	sourcefilename):
		self.SubjectID = SubjectID
		if type(DriveID) is not list:
			DriveID = [DriveID, ]
		self.DriveID = DriveID
		self.roi = roi
		if type(data) is not list:
			data = [data, ]
		self.data = data
		if type(data) is not list:
			sourcefilename = [sourcefilename, ]
		self.sourcefilename = sourcefilename
