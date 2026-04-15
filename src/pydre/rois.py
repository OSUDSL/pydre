from pathlib import Path
from abc import ABC, abstractmethod
from .core import DriveData
import polars as pl
import typing
from typing import Optional
from dataclasses import dataclass
from loguru import logger
from collections.abc import Iterable, Sequence
from polars.exceptions import ColumnNotFoundError


class ROIProcessor(ABC):
    @abstractmethod
    def split(
        self, sourcedrivedata: DriveData
    ) -> Sequence[DriveData]:
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
    except (KeyError, ColumnNotFoundError):
        logger.error("Problem in applying Time ROI to using time column " + column)
        dataframeslice = drive_data
    return dataframeslice


class TimeROI(ROIProcessor):
    rois: dict
    rois_meta: set
    timecol: str

    def __init__(self, filename: Path, timecol: str = "DatTime", **kwargs):
        # parse time filename values
        pl_rois = pl.read_csv(filename)
        roi_list = []
        self.rois = {}
        self.rois_meta = set()
        self.timecol = timecol
        for r in pl_rois.rows(named=True):
            if isinstance(r, dict):
                roi_list.append(r)
            elif isinstance(r, tuple):
                roi_list.append(r._asdict())
        for r in roi_list:
            roi_definition = {}
            meta_values = [r["ROI"]]
            for k, v in r.items():
                if k == "time_start" or k == "time_end":
                    roi_definition[k] = self.parseTimeStamp(v)
                elif k != "ROI":
                    roi_definition[k] = str(v)
                    meta_values.append(str(v))
                    self.rois_meta.add(k)
            roi_name = ":".join(meta_values)
            self.rois[roi_name] = roi_definition

    def split(
        self, sourcedrivedata: DriveData
    ) -> list[DriveData]:
        """
        return list of DriveData objects
        the 'roi' field of the objects will be filled with the roi tag listed
        in the roi definition file column name
        """
        output_list = []
        matching_rois = self.rois.copy()
        if len(self.rois_meta) > 0:
            for k, v in self.rois.items():
                for meta in self.rois_meta:
                    if str(v[meta]) != str(sourcedrivedata.metadata[meta]):
                        del matching_rois[k]
                        break

        for k, v in matching_rois.items():
            start = v["time_start"]
            end = v["time_end"]
            timecol = self.timecol
            new_data = sliceByTime(start, end, timecol, sourcedrivedata.data)
            if new_data.height > 0:
                new_ddata = DriveData(sourcedrivedata, new_data)
                new_ddata.roi = k
                output_list.append(new_ddata)
            else:
                logger.warning(
                    "ROI fails to qualify for {}, ignoring data".format(
                        sourcedrivedata.sourcefilename
                    )
                )
        return output_list

    @staticmethod
    def parseTimeStamp(duration: str | typing.SupportsFloat) -> float:
        # the string will have the format as:
        # hr:min:sec (example 1:15:10)
        # min:sec (example 02:32.34)
        # seconds (example 10.5)

        try:
            float_duration = float(duration)
            return float_duration
        except ValueError:
            duration = str(duration).strip()

        splits = duration.split(":")

        if len(splits) > 3:
            logger.error(
                f"Invalid time format: {duration}. Expected format is hr:min:sec, min:sec, or sec."
            )
            raise ValueError(f"Invalid time format: {duration}")

        if len(splits) == 3:
            hr, min, sec = splits
            time = int(hr) * 60 * 60 + int(min) * 60 + float(sec)
        elif len(splits) == 2:
            min, sec = splits
            time = 60 * int(min) + float(sec)
        else:
            sec = splits[0]
            time = float(sec)
        return time

    @staticmethod
    def from_ranges(ranges, column):
        obj = TimeROI.__new__(TimeROI)
        obj.ranges = ranges
        obj.roi_column = column
        obj.name_prefix = ""
        obj.rois_meta = []
        obj.rois = pl.DataFrame(
            {
                column: [r[0] for r in ranges],
                f"{column}_end": [r[1] for r in ranges],
                "roi": [f"roi{i}" for i in range(len(ranges))],
            }
        )
        return obj


@dataclass
class SpaceROIRegion:
    name: str
    x1: float
    x2: float
    y1: float
    y2: float

    @property
    def xmin(self) -> float:
        return min(self.x1, self.x2)

    @property
    def xmax(self) -> float:
        return max(self.x1, self.x2)

    @property
    def ymin(self) -> float:
        return min(self.y1, self.y2)

    @property
    def ymax(self) -> float:
        return max(self.y1, self.y2)


class SpaceROI(ROIProcessor):
    x_column_name = "XPos"
    y_column_name = "YPos"

    def __init__(self, filename: Path | str, nameprefix: str = "", **kwargs):
        pl_rois = pl.read_csv(filename, has_header=True)

        # Normalize column names to uppercase for case-insensitive matching
        pl_rois = pl_rois.rename({col: col.upper() for col in pl_rois.columns})

        expected_columns = ["ROI", "X1", "X2", "Y1", "Y2"]
        if not set(expected_columns).issubset(set(pl_rois.columns)):
            logger.error(
                f"SpaceROI file {filename} does not contain expected columns {expected_columns}"
            )
            raise ValueError

        coordinate_columns = ["X1", "X2", "Y1", "Y2"]
        try:
            pl_rois = pl_rois.with_columns(
                [pl.col(c).cast(pl.Float64) for c in coordinate_columns]
            )
        except pl.exceptions.InvalidOperationError as e:
            logger.error(f"SpaceROI file {filename} has non-numeric coordinate columns: {e}")
            raise ValueError(f"Coordinate columns must be numeric: {e}") from e

        self.roi_info: list[SpaceROIRegion] = [
            SpaceROIRegion(name=row["ROI"], x1=row["X1"], x2=row["X2"], y1=row["Y1"], y2=row["Y2"])
            for row in pl_rois.rows(named=True)
        ]
        self.name_prefix = nameprefix

    def split(self, sourcedrivedata: DriveData) -> Sequence[DriveData]:
        return_list: list[DriveData] = []

        for region in self.roi_info:
            region_data = sourcedrivedata.data.filter(
                pl.col(self.x_column_name).cast(pl.Float32).is_between(region.xmin, region.xmax)
                & pl.col(self.y_column_name).cast(pl.Float32).is_between(region.ymin, region.ymax)
            )

            if region_data.height == 0:
                logger.warning(
                    "No data for SubjectID: {}, Source: {},  ROI: {}".format(
                        sourcedrivedata.metadata["ParticipantID"],
                        sourcedrivedata.sourcefilename,
                        region.name,
                    )
                )
            else:
                logger.info(
                    "{} Line(s) read into ROI {} for Subject {} From file {}".format(
                        region_data.height,
                        region.name,
                        sourcedrivedata.metadata["ParticipantID"],
                        sourcedrivedata.sourcefilename,
                    )
                )
            new_ddata = DriveData(sourcedrivedata, region_data)
            new_ddata.roi = region.name
            return_list.append(new_ddata)

        return return_list


class ColumnROI(ROIProcessor):
    def __init__(self, columnname: str, **kwargs):
        if not isinstance(columnname, str):
            raise TypeError(f"Expected columnname to be str, got {type(columnname)}")
        self.roi_column = columnname

    def split(self, sourcedrivedata) -> Sequence[DriveData]:
        df = sourcedrivedata.data

        if self.roi_column not in df.columns:
            logger.error(
                f"Column '{self.roi_column}' not found in data for {sourcedrivedata.sourcefilename}"
            )
            raise KeyError(f"ROI column '{self.roi_column}' not found in data")

        df_valid = df.drop_nulls(subset=[self.roi_column])
        if df_valid.is_empty():
            return []

        result = []

        for gname, gdata in df_valid.group_by(self.roi_column):
            roi_name = str(gname[0])
            new_dd = sourcedrivedata.copy()
            new_dd.data = gdata
            new_dd.roi = roi_name
            new_dd.metadata["ROIName"] = roi_name
            result.append(new_dd)

        return result
