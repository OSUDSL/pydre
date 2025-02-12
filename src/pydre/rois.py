import pathlib
from abc import ABCMeta, abstractmethod

import pydre.core
import polars as pl
import re
from loguru import logger
from collections.abc import Iterable


class ROIProcessor(object, metaclass=ABCMeta):
    roi_list = []

    @abstractmethod
    def __init__(self, filename: str | pathlib.Path, nameprefix: str = ""):
        pass

    @abstractmethod
    def split(
        self, sourcedrivedata: pydre.core.DriveData
    ) -> list[pydre.core.DriveData]:
        """Splits the drivedata object according to the ROI specifications.

        Parameters:
            sourcedrivedata: input drivedata object

        Returns:
            list of drivedata objects after splitting
        """
        pass


def sliceByTime(
    begin: float, end: float, column: str, drive_data: pl.DataFrame
) -> pl.DataFrame:
    """
        args:
            begin: float defnining the start point of the slice
            end: float defining the end part of the slice
            column: which column in the drive_data frame to use for the time.  This is usually SimTime or VidTime.
            drive_data: polars DataFrame containing the data to be sliced

        returns:
            polars.DataFrame slice containing requested time slice

    Given a start and end and a column name that represents a time value, output the slice that contains
    only the specified data.
    """
    try:
        dataframeslice = drive_data.filter(
            pl.col(column).is_between(begin, end, closed="left")
        )
    except KeyError:
        logger.error("Problem in applying Time ROI to using time column " + column)
        dataframeslice = drive_data
    return dataframeslice


class TimeROI(ROIProcessor):
    def __init__(self, filename: str | pathlib.Path, timecol: str):
        # parse time filename values
        pl_rois = pl.read_csv(filename)
        rois = []
        self.rois = {}
        self.timecol = timecol
        for r in pl_rois.rows(named=True):
            if isinstance(r, dict):
                rois.append(r)
            elif isinstance(r, tuple):
                rois.append(r._asdict())
        for r in rois:
            roi_name = r["ROI"]
            self.rois[roi_name] = {}
            for k, v in r.items():
                if k != "ROI":
                    self.rois[roi_name][k] = self.parseDuration(v)


    def split(
        self, sourcedrivedata: pydre.core.DriveData
    ) -> list[pydre.core.DriveData]:
        """
        return list of pydre.core.DriveData objects
        the 'roi' field of the objects will be filled with the roi tag listed
        in the roi definition file column name
        """
        # output_list = []
        #
        # if sourcedrivedata.PartID in self.rois.keys():
        #     for roi, duration in self.rois[sourcedrivedata.PartID]:
        #         start, end = duration
        #         new_data = sliceByTime(start, end, timecol, sourcedrivedata.data)
        #         new_ddata = pydre.core.DriveData(sourcedrivedata, new_data)
        #         new_ddata.roi = roi
        #         output_list.append(new_ddata)
        # return output_list
        #
        # if sourcedrivedata.PartID in self.rois.keys():
        #     for roi, duration in self.rois[sourcedrivedata.PartID]:
        #         start, end = duration
        #         new_data = sliceByTime(start, end, timecol, sourcedrivedata.data)
        #         new_ddata = pydre.core.DriveData(sourcedrivedata, new_data)
        #         new_ddata.roi = roi
        #         output_list.append(new_ddata)
        # return output_list
        output_list = []

        for k, v in self.rois.items():
            start = v["time_start"]
            end = v["time_end"]
            timecol = self.timecol
            new_data = sliceByTime(start, end, timecol, sourcedrivedata.data)
            new_ddata = pydre.core.DriveData(sourcedrivedata, new_data)
            new_ddata.roi = k
            output_list.append(new_ddata)
        return output_list



    def parseDuration(self, duration: str) -> float:
        # parse a string indicating duration into a tuple of (starttime, endtime) in seconds
        # the string will have the format as:
        # time1-time2 where time1 or time 2 are either hr:min:sec or min:sec
        # example:  1:15:10-1:20:30
        # example : 02:32-08:45

        # pair_regex = r"([\d:])-([\d:])"
        # time_regex = r"(?:(\d+):)?(\d+):(\d+)"
        # pair_result = re.match(pair_regex, duration)
        # first_time_str, second_time_str = pair_result.group(1, 2)
        # first_time_result = re.match(time_regex, first_time_str)
        # second_time_result = re.match(time_regex, second_time_str)
        # first_time = first_time_result.group(2) * 60 + first_time_result.group(3)
        # if first_time_result.group(1):
        #     first_time += first_time_result.group(1) * 60 * 60
        # second_time = second_time_result.group(2) * 60 + second_time_result.group(3)
        # if second_time_result.group(1):
        #     second_time += second_time_result.group(1) * 60 * 60
        # return (first_time, second_time)

        regex = r'(?:(\d{1,2}):)?(\d{1,2}):(\d{2})'
        pair_result = re.match(regex, duration)
        if pair_result.group(3):
            hr = pair_result.group(1)
            min = pair_result.group(2)
            sec = pair_result.group(3)
            time = int(hr) * 60 * 60 + int(min) * 60 + int(sec)
        else:
            min = pair_result.group(1)
            sec = pair_result.group(2)
            time = 60 * 60 + int(min) * 60 + int(sec)
        return time




class SpaceROI(ROIProcessor):
    x_column_name = "XPos"
    y_column_name = "YPos"

    def __init__(self, filename: str | pathlib.Path, nameprefix: str = ""):
        # parse time filename values
        # roi_info is a data frame containing the cutoff points for the region in each row.
        # It's columns must be roi, X1, X2, Y1, Y2
        pl_rois = pl.read_csv(filename, has_header=True)
        expected_columns = ["roi", "X1", "X2", "Y1", "Y2"]
        if not set(expected_columns).issubset(set(pl_rois.columns)):
            logger.error(
                f"SpaceROI file {filename} does not contain expected columns {expected_columns}"
            )
            raise ValueError
        # convert polars table into dictionary with 'roi' as the key and a dict as the value
        self.roi_info = pl_rois.rows_by_key("roi", unique=True, named=True)
        self.name_prefix = nameprefix

    def split(
        self, sourcedrivedata: pydre.core.DriveData
    ) -> list[pydre.core.DriveData]:
        return_list = []

        for roi_name, roi_location in self.roi_info.items():
            xmin = min(roi_location.get("X1"), roi_location.get("X2"))
            xmax = max(roi_location.get("X1"), roi_location.get("X2"))
            ymin = min(roi_location.get("Y1"), roi_location.get("Y2"))
            ymax = max(roi_location.get("Y1"), roi_location.get("Y2"))

            region_data = sourcedrivedata.data.filter(
                pl.col(self.x_column_name).cast(pl.Float32).is_between(xmin, xmax)
                & pl.col(self.y_column_name).cast(pl.Float32).is_between(ymin, ymax)
            )

            if region_data.height == 0:
                # try out PartID to get this to run cgw 5/20/2022
                # logger.warning("No data for SubjectID: {}, Source: {},  ROI: {}".format(
                #    ddata.SubjectID,
                #    ddata.sourcefilename,
                #    self.roi_info.roi[i]))
                logger.warning(
                    "No data for SubjectID: {}, Source: {},  ROI: {}".format(
                        sourcedrivedata.metadata["ParticipantID"], sourcedrivedata.sourcefilename, roi_name
                    )
                )
            else:
                # try out PartID to get this to run cgw 5/20/2022
                # logger.info("{} Line(s) read into ROI {} for Subject {} From file {}".format(
                #     len(region_data),
                #     self.roi_info.roi[i],
                #     ddata.SubjectID,
                #     ddata.sourcefilename))
                logger.info(
                    "{} Line(s) read into ROI {} for Subject {} From file {}".format(
                        region_data.height,
                        roi_name,
                        sourcedrivedata.metadata["ParticipantID"],
                        sourcedrivedata.sourcefilename
                    )
                )
            new_ddata = pydre.core.DriveData(sourcedrivedata, region_data)
            new_ddata.roi = roi_name
            return_list.append(new_ddata)

        return return_list


class ColumnROI(ROIProcessor):
    def __init__(self, columnname: str, nameprefix=""):
        # parse time filename values
        self.roi_column = columnname
        self.name_prefix = nameprefix

    def split(
        self, sourcedrivedata: pydre.core.DriveData
    ) -> Iterable[pydre.core.DriveData]:
        return_list = []

        for gname, gdata in sourcedrivedata.data.group_by(self.roi_column):
            gname = gname[0]
            if gname != pl.Null:
                new_ddata = pydre.core.DriveData(sourcedrivedata, gdata)
                new_ddata.roi = str(gname)
                return_list.append(new_ddata)
        return return_list
