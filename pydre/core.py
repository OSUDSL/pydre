# -*- coding: utf-8 -*-

import pandas
import logging
import sys
import typing

from typing import List

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
        logger.error(
            " Data file(-d) invalid. Data frame slice could not be created. Please check contents of file for \"VidTime\" column.")
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
            logger.warning(
                "Subject {} roi {} contains  more than one DataFrame. Only the first element will be in the merged output.".format(
                    drivedata.PartID, DriveData.roi))

        subject = tomerge[0].PartID
        driveIDs = tomerge[0].DriveID
        roi = tomerge[0].roi
        sources = list(tomerge[0].sourcefilename)

        out_frame = tomerge[0].data[0]
        if (len(tomerge) > 1):
            i = 0
            while i < len(tomerge) - 1:
                i = i + 1

                # This part sets up data to be included in the final Drive Data object
                if tomerge[i].PartID != subject:
                    logger.warning(
                        "Merging data for multiple subjects {} and {}. Only the first will be used".format(subject,
                                                                                                           tomerge[
                                                                                                               i].PartID))
                driveIDs.append(list(tomerge[i].DriveID))  # Some may be added twice. Is this desireable?
                if tomerge[i].roi != roi:
                    logger.warning("Merging data for multiple rois {} and {}. Only the first will be used.".format(roi,
                                                                                                                   tomerge[
                                                                                                                       i].roi))
                sources.append(list(tomerge[i].sourcefilename))

                # This part does the actual merging
                last_line = out_frame.tail(1)
                last_x = last_line.XPos.iloc[0]
                last_y = last_line.YPos.iloc[0]
                last_time = last_line.SimTime.iloc[0]
                next_frame = tomerge[i].data[0]
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

        return DriveData(subject, driveIDs, roi, out_frame, sources)
    pass


class DriveData:

    def __init__(self, PartID: typing.Optional[int], DriveID: typing.Optional[int], roi: typing.Optional[str],
                 data: pandas.DataFrame, sourcefilename: typing.Optional[str], UniqueID: typing.Optional[int],
                 scenarioName: typing.Optional[str], mode: typing.Optional[str]):

        self.PartID = PartID
        self.DriveID = DriveID
        self.roi = roi
        self.data = data
        self.sourcefilename = sourcefilename
        self.UniqueID = UniqueID
        self.scenarioName = scenarioName
        self.mode = mode

        # format_identifier -1: this drivedata object is missing at least 1 required field or contains error
        # format_identifier 0: this drivedata object was created from an old format data file
        # format_identifier 1: this drivedata object was created from a new format data file ([mode]_[participant id]_[scenario name]_[uniquenumber].dat)
        if DriveID >= 0:
            self.format_identifier = 0
        elif len(scenarioName) > 0:
            self.format_identifier = 1
        else:
            self.format_identifier = -1

    def checkColumns(self, required_columns: List[str]):
        difference = set(required_columns) - set(list(self.data.columns))
        if len(difference) > 0:
            raise ColumnsMatchError(difference)


# ------ exception handling ------

def funcName():  #:return: name of caller
    return sys._getframe(1).f_code.co_name

    # @contextmanager
    # def disable_exception_traceback():
    """
    All traceback information is suppressed and only the exception type and value are printed
    """


#    default_value = getattr(sys, "tracebacklimit", 1000)  # `1000` is Python's default value
#    sys.tracebacklimit = 0
#    yield
#    sys.tracebacklimit = default_value  # revert changes

# def columnException(drivedata, required_col):
#    diff = drivedata.checkColumns(required_col)
#    if (len(diff) > 0):
#        with disable_exception_traceback():
#            raise ColumnsMatchError("Can't find needed columns " + str(diff) + " in data file " + drivedata.sourcefilename)


class ColumnsMatchError(Exception):
    pass
