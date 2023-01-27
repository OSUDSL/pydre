# -*- coding: utf-8 -*-

import pydre.core
import polars as pl
import csv
import re
import logging

logger = logging.getLogger(__name__)


def sliceByTime(begin: float, end: float, column: str, drive_data: pl.DataFrame):
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
                        #if (item.SubjectID == subject and driveID in item.DriveID): # try out PartID to get this to run cgw 5/20/2022
                        if (item.PartID == subject and driveID in item.DriveID):
                            new_ddata = pydre.core.sliceByTime(
                                start_time, end_time, "VidTime", item.data[0])
                            new_ddata.copyMetaData(ddata)
                            new_ddata.roi = titles[roi]
                            outputs.append(new_ddata)

                            drives.append(item.DriveID)
                            source_files.append(item.sourcefilename)
                            break
                if len(drives) == 0:
                    logger.warning("No data for ROI (subject: {}, roi: {})".format(
                        subject, titles[roi]))
                else:
                    new_ddata = pydre.core.DriveData(data_frame, ddata.sourcefilename)
                    new_ddata.copyMetaData(ddata)
                    new_ddata.roi = titles[roi]
                    outputs.append(new_ddata)
                    outputs.append(pydre.core.DriveData(
                        subject, drives, titles[roi], data_frame, source_files))
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
            elif isinstance(r, NamedTuple):
                self.roi_info.append(r._asdict())
        self.name_prefix = nameprefix

    def split(self, datalist):
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
                #region_data = ddata.data

                region_data = ddata.data[(ddata.data.XPos < xmax) &
                                       (ddata.data.XPos > xmin) &
                                       (ddata.data.YPos < ymax) &
                                       (ddata.data.YPos > ymin)]
                if (len(region_data) == 0):

                    # try out PartID to get this to run cgw 5/20/2022
                    # logger.warning("No data for SubjectID: {}, Source: {},  ROI: {}".format(
                    #    ddata.SubjectID,
                    #    ddata.sourcefilename,
                    #    self.roi_info.roi[i]))
                    logger.warning("No data for SubjectID: {}, Source: {},  ROI: {}".format(
                        ddata.PartID,
                        ddata.sourcefilename,
                        self.roi_info.roi[i]))
                else:
                    # try out PartID to get this to run cgw 5/20/2022
                    # logger.info("{} Line(s) read into ROI {} for Subject {} From file {}".format(
                    #     len(region_data),
                    #     self.roi_info.roi[i],
                    #     ddata.SubjectID,
                    #     ddata.sourcefilename))
                    logger.info("{} Line(s) read into ROI {} for Subject {} From file {}".format(
                        len(region_data),
                        self.roi_info.roi[i],
                        ddata.PartID,
                        ddata.sourcefilename))
                new_ddata = pydre.core.DriveData(region_data, ddata.sourcefilename)
                new_ddata.copyMetaData(ddata)
                new_ddata.roi = self.roi_info.roi[i]
                return_list.append(new_ddata)

        return return_list


class ColumnROI():

    def __init__(self, columnname, nameprefix=""):
        # parse time filename values
        self.roi_column = columnname
        self.name_prefix = nameprefix

    def split(self, datalist):
        """
        return list of pydre.core.DriveData objects
        the 'roi' field of the objects will be filled with the roi tag listed
        in the roi definition file column name
        """
        return_list = []
        for ddata in datalist:
            split_list = ddata.partition_by(self.roi_column)
            for subData in split_list:
                roi_value = subData.get_column(self.roi_column)[0]
                if roi_value != pl.Null:
                    new_ddata = pydre.core.DriveData(subData, ddata.sourcefilename)
                    new_ddata.copyMetaData(ddata)
                    new_ddata.roi = roi_value
                    return_list.append(new_ddata)
        return return_list
