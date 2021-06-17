# -*- coding: utf-8 -*-

import pandas
import logging
import sys

from contextlib import contextmanager
from inspect import currentframe, getframeinfo
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
	try:
		dataframeslice = drive_data[(drive_data[column] >= begin) & (drive_data[column] <= end)]
	except KeyError:
		logger.error(" Data file(-d) invalid. Data frame slice could not be created. Please check contents of file for \"VidTime\" column.")
		sys.exit(1)
	return dataframeslice


def mergeBySpace(tomerge: list):
	"""
		args:
			tomerge: list of DriveData objects to merge

		returns:
			DriveData object containing merged data and Drive ID of first element in the tomerge list

		Takes the first DriveData in 'tomerge', finds the last X and Y position, matches the closest X and Y
		position in the next DriveData object in 'tomerge'.  The time stamps for the second data list are
		altered appropriately.
		This repeats for all elements in 'tomerge'.
	"""
	for drivedata in tomerge:
		if (len(drivedata.data) > 1):
			logger.warning("Subject {} roi {} contains  more than one DataFrame. Only the first element will be in the merged output.".format(drivedata.PartID, DriveData.roi))
		
		subject = tomerge[0].PartID
		driveIDs = tomerge[0].DriveID
		roi = tomerge[0].roi
		sources = list(tomerge[0].sourcefilename)
		
		out_frame = tomerge[0].data[0]
		if (len(tomerge) > 1):
			i = 0
			while i < len(tomerge) - 1:
				i = i + 1
				
				#This part sets up data to be included in the final Drive Data object
				if tomerge[i].PartID != subject:
					logger.warning("Merging data for multiple subjects {} and {}. Only the first will be used".format(subject, tomerge[i].PartID))
				driveIDs.append(list(tomerge[i].DriveID)) #Some may be added twice. Is this desireable?
				if tomerge[i].roi != roi:
					logger.warning("Merging data for multiple rois {} and {}. Only the first will be used.".format(roi, tomerge[i].roi))
				sources.append(list(tomerge[i].sourcefilename))
				
				#This part does the actual merging
				last_line = out_frame.tail(1)
				last_x = last_line.XPos.iloc[0]
				last_y = last_line.YPos.iloc[0]
				last_time = last_line.SimTime.iloc[0]
				next_frame = tomerge[i].data[0]
				min_dist = float('inf')
				min_index = 0
				for index, row in next_frame.iterrows():
					dist = (row.XPos - last_x)**2 + (row.YPos - last_y)**2
					if (dist < min_dist):
						min_index = index
						min_dist = dist
				start_time = next_frame.iloc[min_index].SimTime
				next_frame = next_frame[min_index:]
				next_frame.SimTime += last_time - start_time
				out_frame = out_frame.append(next_frame)
				
		return DriveData(subject, driveIDs, roi, out_frame, sources)
	pass

class DriveData:

	def __init__(self, PartID: int, DriveID,	roi: str, data,	sourcefilename):
		self.PartID = PartID
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

	def checkColumns(self, col):
		expected_col = col
		difference = []
		for df in self.data:
			df_col = (df.columns).tolist()
			if (len(expected_col) != len(df_col)):
				#logger.error("The numbers of columns do not match")
				difference = set(expected_col) - set(df_col)
				break
			elif (expected_col.sort() != df_col.sort()):
				#logger.error("Columns do not match")
				difference = set(expected_col) - set(df_col)
				break
		return difference

# ------ exception handling ------
@contextmanager
def disable_exception_traceback():
    """
    All traceback information is suppressed and only the exception type and value are printed
    """
    default_value = getattr(sys, "tracebacklimit", 1000)  # `1000` is Python's default value
    sys.tracebacklimit = 0
    yield
    sys.tracebacklimit = default_value  # revert changes

def columnException(drivedata, required_col):
    diff = drivedata.checkColumns(required_col)
    if (len(diff) > 0):
        with disable_exception_traceback():
            raise ColumnsMatchError("Can't find needed columns " + str(diff) + " in data file " + drivedata.sourcefilename)
	

class ColumnsMatchError(Exception):
	pass