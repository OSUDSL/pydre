from __future__ import annotations

import polars
from loguru import logger
import sys
from typing import List, Optional


class DriveData:
    data: polars.dataframe
    sourcefilename: str
    roi: Optional[str]
    format_identifier: int
    PartID: Optional[int]
    DriveID: Optional[int]
    UniqueID: Optional[int]
    scenarioName: Optional[int]
    mode: Optional[int]

    def __init__(self, data: polars.DataFrame, sourcefilename: Optional[str]):
        self.data = data
        self.sourcefilename = sourcefilename
        self.roi = None
        self.format_identifier = -1

    @classmethod
    def initV2(
            cls,
            data: polars.DataFrame,
            sourcefilename: str,
            PartID: Optional[int],
            DriveID: Optional[int],
    ):
        obj = cls(data, sourcefilename)
        obj.PartID = PartID
        obj.DriveID = DriveID
        obj.format_identifier = 2
        return obj

    @classmethod
    def initV4(
            cls,
            data: polars.DataFrame,
            sourcefilename: str,
            PartID: str,
            UniqueID: Optional[int],
            scenarioName: Optional[str],
            mode: Optional[str],
    ):
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

    def checkColumns(self, required_columns: List[str]) -> None:
        difference = set(required_columns) - set(list(self.data.columns))
        if len(difference) > 0:
            raise polars.exceptions.ColumnNotFoundError("Columns {} not found.".format(difference))

    def checkColumnsNumeric(self, columns: List[str]) -> Optional[List[str]]:
        # check numeric for a list
        # returns list with any columns from `columns` that are non-numeric
        non_numeric = []
        for column in columns:
            if column in self.data:
                to_check = self.data.get_column(column)
                if not to_check.dtype.is_numeric():
                    logger.warning(
                        "col("
                        + column
                        + ") is not numeric in "
                        + self.sourcefilename
                    )
                    non_numeric.append(column)
            else:
                logger.warning(
                    column + " in " + self.sourcefilename + " does not exist."
                )
                non_numeric.append(column)
        if len(non_numeric) > 0:
            raise polars.exceptions.PolarsError("Columns {} not numeric.".format(non_numeric))


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
