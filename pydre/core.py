# -*- coding: utf-8 -*-

from __future__ import annotations

import pandas
import logging
import sys
import typing
from typing import List

logger = logging.getLogger(__name__)

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
    out_frame = tomerge[0].data

    if len(tomerge) > 1:
        i = 0
        while i < len(tomerge) - 1:
            i = i + 1

            # This part does the actual merging
            last_line = out_frame.tail(1)
            last_x = last_line.XPos.iloc[0]
            last_y = last_line.YPos.iloc[0]
            last_time = last_line.SimTime.iloc[0]
            next_frame = tomerge[i].data
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

    new_dd = DriveData(out_frame, "")
    new_dd.copyMetaData(tomerge[0])
    return new_dd


class DriveData:

    def __init__(self, data: pandas.DataFrame, sourcefilename: typing.Optional[str]):
        self.data = data
        self.sourcefilename = sourcefilename
        self.roi = None
        self.format_identifier = -1

    @classmethod
    def initV2(cls, data: pandas.DataFrame, sourcefilename: str, PartID: typing.Optional[int],
               DriveID: typing.Optional[int]):
        obj = cls(data, sourcefilename)
        obj.PartID = PartID
        obj.DriveID = DriveID
        obj.format_identifier = 2
        return obj

    @classmethod
    def initV4(cls, data: pandas.DataFrame, sourcefilename: str, PartID: str, UniqueID: typing.Optional[int],
               scenarioName: typing.Optional[str], mode: typing.Optional[str]):
        obj = cls(data, sourcefilename)
        obj.PartID = PartID
        obj.UniqueID = UniqueID
        obj.scenarioName = scenarioName
        obj.mode = mode
        obj.format_identifier = 4
        return obj

    def copyMetaData(self, other: DriveData):
        self.sourcefilename = other.sourcefilename
        self.PartID = other.PartID
        if other.format_identifier == 2:
            self.DriveID = other.DriveID
        elif other.format_identifier == 4:
            self.UniqueID = other.UniqueID
            self.scenarioName = other.scenarioName
            self.mode = other.mode
        self.format_identifier = other.format_identifier


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
    def __init__(self, missing_columns):
        self.missing_columns = missing_columns
