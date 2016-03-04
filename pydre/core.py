# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


def sliceByTime(begin, end, column, drive_data):
	"""
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
