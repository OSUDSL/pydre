# -*- coding: utf-8 -*-

import pydre.core
import polars as pl
import csv
import re
import logging

logger = logging.getLogger(__name__)

from collections.abc import Iterable

def sliceByTime(begin: float, end: float, column: str, drive_data: pl.DataFrame) -> pl.DataFrame:
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
        dataframeslice = drive_data.filter(pl.col(column).is_between(begin, end, include_bounds=(True, False)))
    except KeyError:
        logger.error(
            "Problem applying Time ROI to data file using column " + column)
        sys.exit(1)
    return dataframeslice

class TimeROI():

    def __init__(self, filename, nameprefix=""):
        # parse time filename values

        pl_rois = pl.read_csv(filename)
        rois = []
        self.rois = {}
        for r in pl_rois.rows(named=True):
            if isinstance(r, dict):
                rois.append(r)
            elif isinstance(r, tuple):
                rois.append(r._asdict())
        for r in rois:
            participant = r["Participant"]
            self.rois[participant] = {}
            for k,v in r:
                if k != "Participant":
                    self.rois[participant][k] = self.parseDuration(v)
        self.name_prefix = nameprefix

    def split(self, datalist: list[pydre.core.DriveData]) -> list[pydre.core.DriveData]:
        """
        return list of pydre.core.DriveData objects
        the 'roi' field of the objects will be filled with the roi tag listed
        in the roi definition file column name
        """
        timecol = "SimTime"
        output_list = []
        for ddata in datalist:
            if ddata.PartID is in self.rois.keys():
                for roi, duration in self.rois[ddata.PartID]:
                    start, end = duration
                    new_data = sliceByTime(start, end, timecol, ddata.data)
                    new_ddata = pydre.core.DriveData(new_data, ddata.sourcefilename)
                    new_ddata.copyMetaData(ddata)
                    new_ddata.roi = roi
                    output_list.append(new_ddata)
        return output_list


    def parseDuration(self, duration: str) -> tuple[float, float]:
        # parse a string indicating duration into a tuple of (starttime, endtime) in seconds
        # the string will have the format as:
        # time1-time2 where time1 or time 2 are either hr:min:sec or min:sec
        # example:  1:15:10-1:20:30
        # example : 02:32-08:45
        pair_regex = r"([\d:])-([\d:])"
        time_regex = r"(?:(\d+):)?(\d+):(\d+)"
        pair_result = re.match(pair_regex, duration)
        first_time_str, second_time_str = pair_result.group(1, 2)
        first_time_result = re.match(time_regex, first_time_str)
        second_time_result = re.match(time_regex, second_time_str)
        first_time = first_time_result.group(2) * 60 + first_time_result.group(3)
        if first_time_result.group(1):
            first_time += first_time_result.group(1) * 60*60
        second_time = second_time_result.group(2) * 60 + second_time_result.group(3)
        if second_time_result.group(1):
            second_time += second_time_result.group(1) * 60*60
        return (first_time, second_time)


class SpaceROI():

    def __init__(self, filename, nameprefix=""):
        # parse time filename values
        # roi_info is a data frame containing the cutoff points for the region in each row.
        # It's columns must be roi, X1, X2, Y1, Y2
        pl_rois = pl.read_csv(filename)
        self.roi_info = []
        for r in pl_rois.rows(named=True):
            if isinstance(r, dict):
                self.roi_info.append(r)
            elif isinstance(r, tuple):
                self.roi_info.append(r._asdict())
        self.name_prefix = nameprefix

    def split(self, datalist: list[pydre.core.DriveData]):
        """
        return list of pydre.core.DriveData objects
        the 'roi' field of the objects will be filled with the roi tag listed
        in the roi definition file column name
        """
        return_list = []

        for roi in self.roi_info:
            for ddata in datalist:
                xmin = min(roi.get("X1"), roi.get("X2"))
                xmax = max(roi.get("X1"), roi.get("X2"))
                ymin = min(roi.get("Y1"), roi.get("Y2"))
                ymax = max(roi.get("Y1"), roi.get("Y2"))

                region_data = ddata.data.filter(pl.col("XPos").is_between(xmin, xmax) &
                                                pl.col("YPos").is_between(ymin, ymax))

                if (region_data.height == 0):
                    # try out PartID to get this to run cgw 5/20/2022
                    # logger.warning("No data for SubjectID: {}, Source: {},  ROI: {}".format(
                    #    ddata.SubjectID,
                    #    ddata.sourcefilename,
                    #    self.roi_info.roi[i]))
                    logger.warning("No data for SubjectID: {}, Source: {},  ROI: {}".format(
                        ddata.PartID,
                        ddata.sourcefilename,
                        roi))
                else:
                    # try out PartID to get this to run cgw 5/20/2022
                    # logger.info("{} Line(s) read into ROI {} for Subject {} From file {}".format(
                    #     len(region_data),
                    #     self.roi_info.roi[i],
                    #     ddata.SubjectID,
                    #     ddata.sourcefilename))
                    logger.info("{} Line(s) read into ROI {} for Subject {} From file {}".format(
                        region_data.height,
                        roi,
                        ddata.PartID,
                        ddata.sourcefilename))
                new_ddata = pydre.core.DriveData(region_data, ddata.sourcefilename)
                new_ddata.copyMetaData(ddata)
                new_ddata.roi = roi.get("roi")
                return_list.append(new_ddata)

        return return_list


class ColumnROI():

    def __init__(self, columnname: str, nameprefix=""):
        # parse time filename values
        self.roi_column = columnname
        self.name_prefix = nameprefix

    def split(self, datalist: Iterable[pydre.core.DriveData]) -> Iterable[pydre.core.DriveData]:
        """
        return list of pydre.core.DriveData objects
        the 'roi' field of the objects will be filled with the roi tag listed
        in the roi definition file column name
        """
        return_list = []
        for ddata in datalist:
            groups = ddata.groupby(self.roi_column)
            for gname, gdata in groups:
                if gname != pl.Null:
                    new_ddata = pydre.core.DriveData(gdata, ddata.sourcefilename)
                    new_ddata.roi = gname
                    return_list.append(new_ddata)
        return return_list
