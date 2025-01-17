from __future__ import annotations

import copy
import re

import polars
from loguru import logger
from typing import List, Optional, Any
from pathlib import Path

class DriveData:
    data: polars.DataFrame
    sourcefilename: Path
    sourcefiletype: Optional[str]
    roi: Optional[str]
    metadata: dict[str, Any]

    def __init__(self, orig: DriveData = None, newdata: Optional[polars.DataFrame] = None):
        if orig is not None:
            if newdata is not None:
                self.data = newdata
            else:
                self.data = copy.deepcopy(orig.data)
            self.roi = orig.roi
            self.sourcefilename = orig.sourcefilename
            self.sourcefiletype = orig.sourcefiletype
            self.metadata = copy.deepcopy(orig.metadata)
        else:
            self.data = polars.DataFrame()
            self.roi = None
            self.sourcefilename = Path()
            self.sourcefiletype = None
            self.metadata = {}


    @classmethod
    def init_test(
            cls,
            data: polars.DataFrame,
            sourcefilename: Path
    ):
        """Initializes a DriveData object with a given sourcefilename and data. Used for testing."""
        obj = cls()
        obj.sourcefilename = sourcefilename
        obj.data = data
        return obj


    @classmethod
    def init_old_rti(
        cls,
        sourcefilename: Path
    ):
        obj = cls()
        obj.sourcefilename = sourcefilename
        datafile_re_format0 = re.compile(
            r"([^_]+)_Sub_(\d+)_Drive_(\d+)(?:.*).dat"
        )
        match_format0 = datafile_re_format0.search(str(sourcefilename))
        scenario, PartID, DriveID = match_format0.groups()
        obj.metadata["ParticipantID"] = PartID
        obj.metadata["DriveID"] = DriveID
        obj.sourcefiletype = "old SimObserver"
        return obj

    @classmethod
    def init_rti(
        cls,
        sourcefilename: Path
    ):
        obj = cls()
        obj.sourcefilename = sourcefilename
        datafile_re_format1 = re.compile(
            r"([^_]+)_([^_]+)_([^_]+)_(\d+)(?:.*).dat"
        )  # [mode]_[participant id]_[scenario name]_[uniquenumber].dat
        match_format1 = datafile_re_format1.search(str(sourcefilename))
        mode, subject_id, scen_name, unique_id = match_format1.groups()
        obj.metadata["ParticipantID"] = subject_id
        obj.metadata["UniqueID"] = unique_id
        obj.metadata["ScenarioName"] = scen_name
        obj.metadata["DXmode"] = mode
        obj.sourcefiletype = "SimObserver r2"
        return obj

    @classmethod
    def init_scanner(cls, sourcefilename: Path):
        obj = cls()
        obj.sourcefilename = sourcefilename
        datafile_re_format_lboro = re.compile(r"[pP](\d+)[vV](\d+)[dD](\d+).*")
        match_format_lboro = datafile_re_format_lboro.search(str(sourcefilename))
        subject_id, visit_id, drive_id = match_format_lboro.groups()
        obj.metadata["ParticipantID"] = subject_id
        obj.metadata["VisitID"] = visit_id
        obj.metadata["DriveID"] = drive_id
        return obj


    def loadData(self):
        if self.sourcefiletype == "old SimObserver":
            self.__load_datfile()
        elif self.sourcefiletype == "SimObserver r2":
            self.__load_datfile()
        elif self.sourcefiletype == "Scanner":
            self.__load_scannerfile()

    def __load_datfile(self) -> pydre.core.DriveData:
        """Load a single .dat file (space delimited csv) """
        self.data = polars.read_csv(
            self.sourcefilename,
            separator=" ",
            null_values=".",
            truncate_ragged_lines=True,
            infer_schema_length=5000,
        )

    def __load_scannerfile(self):
        """Load a single csv file containing data from the Scanners simulator"""
        self.data = polars.read_csv(
            self.sourcefilename,
            delimiter="\t",
            null_values="null",
            truncate_ragged_lines=True,
        )

    def copyMetaData(self, other: DriveData):
        self.sourcefilename = other.sourcefilename
        self.sourcefiletype = other.sourcefiletype
        self.roi = other.roi
        self.metadata = copy.deepcopy(other.metadata)

    def checkColumns(self, required_columns: List[str]) -> None:
        difference = set(required_columns) - set(list(self.data.columns))
        if len(difference) > 0:
            raise ColumnsMatchError(
                f"Columns {difference} not found.", list(difference)
            )

    def checkColumnsNumeric(self, columns: List[str]) -> None:
        """Scans data for required column. If columns do not exist or are not numeric, raise an exception.

        args:
            columns: List of required numeric columns.
        """
        non_numeric = []
        for column in columns:
            if column in self.data:
                to_check = self.data.get_column(column)
                if not to_check.dtype.is_numeric():
                    logger.info(
                        "col("
                        + column
                        + ") is not numeric in "
                        + str(self.sourcefilename)
                    )
                    non_numeric.append(column)
            else:
                logger.info(
                    column + " in " + str(self.sourcefilename) + " does not exist."
                )
                non_numeric.append(column)
        if len(non_numeric) > 0:
            raise ColumnsMatchError(f"Columns {non_numeric} not numeric.", non_numeric)


## TODO: Update this to polars style.
# def mergeBySpace(tomerge: List[DriveData]) -> DriveData:
#     """
#     args:
#         tomerge: list of DriveData objects to merge
#
#     returns:
#         DriveData object containing merged data and Drive ID of first element in the tomerge list
#
#     Takes the first DriveData in 'tomerge', finds the last X and Y position, matches the closest X and Y
#     position in the next DriveData object in 'tomerge'.  The time stamps for the second data list are
#     altered appropriately.
#     This repeats for all elements in 'tomerge'.
#     """
#     out_frame = tomerge[0].data
#
#     if len(tomerge) > 1:
#         i = 0
#         while i < len(tomerge) - 1:
#             i = i + 1
#
#             # This part does the actual merging
#             last_line = out_frame.tail(1)
#             last_x = last_line.XPos.iloc[0]
#             last_y = last_line.YPos.iloc[0]
#             last_time = last_line.SimTime.iloc[0]
#             next_frame = tomerge[i].data
#             min_dist = float("inf")
#             min_index = 0
#             for index, row in next_frame.iterrows():
#                 dist = (row.XPos - last_x) ** 2 + (row.YPos - last_y) ** 2
#                 if dist < min_dist:
#                     min_index = index
#                     min_dist = dist
#             start_time = next_frame.iloc[min_index].SimTime
#             next_frame = next_frame[min_index:]
#             next_frame.SimTime += last_time - start_time
#             out_frame = out_frame.append(next_frame)
#
#     new_dd = DriveData(out_frame, "")
#     new_dd.copyMetaData(tomerge[0])
#     return new_dd
#


# ------ exception handling ------


class ColumnsMatchError(Exception):
    """Exception when a filter or metric expects a certain column in DriveData but it is not present or an unexpected type"""

    default_message = "Columns in DriveData object not as expected."

    def __init__(self, message: str, missing_columns: list[str]):
        super().__init__(message or f"{self.default_message} {missing_columns}")
        self.missing_columns = missing_columns
