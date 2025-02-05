import datetime
import struct
from loguru import logger
from pathlib import Path
import polars as pl
import pydre.core
from typing import Optional
from . import registerFilter
import jenkspy


@registerFilter()
def numberBinaryBlocks(
    drivedata: pydre.core.DriveData,
    binary_column="ButtonStatus",
    new_column="NumberedBlocks",
    only_on=0,
    limit_fill_null=700,
    extend_blocks=0,
) -> pydre.core.DriveData:
    """Adds a column that separates data into blocks based on the value of another column

    If only_on is set to 1, it filters the data to only include rows where binary_col is set to 1.
    If extend_blocks is set to 1, it extends the blocks.

    Parameters:
        binary_column: The name of the column to reference
        new_column: The name of the new column with blocks
        only_on: Determines whether to filter the data after adding blocks.
        extend_blocks: Determines whether to extend the blocks.
        limit_fill_null: Determines how many rows to fill using fill_null (only applies when extend_blocks is set to 1).

    Returns:
        Original drive data object augmented with new column
    """

    required_col = [binary_column]
    drivedata.checkColumns(required_col)

    new_dd = drivedata.data.with_columns(
        (pl.col(binary_column).shift() != pl.col(binary_column))
        .cum_sum()
        .alias(new_column))

    # drivedata.data.hstack(blocks, in_place=True)
    if only_on:
        try:
            new_dd = new_dd.filter(pl.col(binary_column) == 1)
            new_dd = new_dd.with_columns((pl.col(new_column)+1.0)/2.0)
        except pl.exceptions.ComputeError as e:
            logger.warning(
                "Assumed binary column {} in {} has non-numeric value.".format(
                    binary_column, drivedata.sourcefilename
                )
            )

    if extend_blocks:
        new_dd = new_dd.with_columns(
            pl.when(pl.col(binary_column) == 0)
            .then(None)
            .otherwise(pl.col(new_column))
            .alias(new_column)
        )
        new_dd = new_dd.with_columns(
            pl.col(new_column).fill_null(strategy="forward", limit=limit_fill_null)
        )
        new_dd = new_dd.filter(pl.col(new_column).is_not_null())

    drivedata.data = new_dd
    return drivedata

@registerFilter()
def Jenks(
    drivedata: pydre.core.DriveData, oldCol: str, newCol: str
) -> pydre.core.DriveData:
    """
    Classifies the given column using Jenks natural breaks and outputs a binary column.

    Parameters:
        drivedata: The DriveData object containing the data.
        oldCol: The name of the column to classify (should be 'headPitch').
        newCol: The name of the new binary column to be created (e.g., 'hpBinary').

    Returns:
        Updated DriveData object with the new binary column.
    """
    # Ensure the required column exists
    required_col = [oldCol]
    drivedata.checkColumns(required_col)

    # Extract the data from the specified column
    head_pitch_values = drivedata.data[oldCol].to_list()

    # Determine Jenks breaks
    breaks = jenkspy.jenks_breaks(head_pitch_values, n_classes=2)

    # Assign binary values based on the breaks
    new_data = drivedata.data.with_columns(
        pl.when(pl.col(oldCol) <= breaks[1])
        .then(0)
        .otherwise(1)
        .alias(newCol)
    )

    drivedata.data = new_data
    return drivedata


@registerFilter()
def SimTimeFromDatTime(drivedata: pydre.core.DriveData) -> pydre.core.DriveData:
    """Copies DatTime to SimTime

    Note: Requires data columns
        - SimTime: simulation time
        = DatTime: time from simobserver recording start

    Returns:
        Original DriveData object with identical DatTime and SimTime
    """
    drivedata.data = drivedata.data.with_columns(pl.col("DatTime").alias("SimTime"))
    return drivedata


@registerFilter()
def FixReversedRoadLinearLand(drivedata: pydre.core.DriveData) -> pydre.core.DriveData:
    """Fixes a section of reversed road in the LinearLand map

    RoadOffset becomes -RoadOffset between XPos 700 and 900

    Note: Requires data columns
        - XPos: X position of ownship
        - RoadOffset: lateral distance on roadway

    Returns:
        Original DriveData object with altered RoadOffset column data
    """
    drivedata.data = drivedata.data.with_columns(
        pl.when(pl.col("XPos").cast(pl.Float32).is_between(700, 900))
        .then(-(pl.col("RoadOffset").cast(pl.Float32)))
        .otherwise(pl.col("RoadOffset").cast(pl.Float32))
        .alias("RoadOffset")
    )
    return drivedata


@registerFilter()
def setinrange(
    drivedata: pydre.core.DriveData,
    coltoset: str,
    valtoset: float,
    colforrange: str,
    rangemin: float,
    rangemax: float,
) -> pydre.core.DriveData:
    """Set values of one column based on the values of another column

    If the value of *colforrange* is outside the range of (*rangemin*, *rangemax*), then
    the value of *coltoset* will be unchanged. Otherwise, the value of *coltoset* will be changed to *valtoset*.

    Parameters:
        coltoset: The name of the column to modify
        valtoset: The new value to set for the
        colforrange: The name of the column to look up to decide to set a new value or not
        rangemin: Minimum value of the range
        rangemax: Maximum value of the range

    Returns:
        Original DriveData object with modified column
    """
    drivedata.data = drivedata.data.with_columns(
        pl.when(pl.col(colforrange).cast(pl.Float32).is_between(rangemin, rangemax))
        .then(valtoset)
        .otherwise(pl.col(coltoset))
        .cast(pl.Float32)
        .alias(coltoset)
    )

    return drivedata


@registerFilter()
def relativeBoxPos(drivedata: pydre.core.DriveData) -> pydre.core.DriveData:
    start_x = drivedata.data.get_column("XPos").min()
    drivedata.data = drivedata.data.with_columns(
        [
            (pl.col("BoxPosY").cast(pl.Float32) - start_x)
            .clip(lower_bound=0)
            .alias("relativeBoxStart")
        ]
    )
    return drivedata


@registerFilter()
def zscoreCol(
    drivedata: pydre.core.DriveData, col: str, newcol: str
) -> pydre.core.DriveData:
    """Transform a column into a standardized z-score column

    Parameters:
        col: The name of the column to transform
        newcol: The name of the new z-score column

    Returns:
        Original DriveData object augmented with new z-score column
    """
    colMean = drivedata.data.get_column(col).mean()
    colSD = drivedata.data.get_column(col).std()
    drivedata.data = drivedata.data.with_columns(
        ((pl.col(col) - colMean) / colSD).alias(newcol)
    )
    return drivedata


@registerFilter()
def speedLimitTransitionMarker(
    drivedata: pydre.core.DriveData, speedlimitcol: str
) -> pydre.core.DriveData:
    speedlimitpos = drivedata.data.select(
        [
            (pl.col(speedlimitcol).shift() != pl.col(speedlimitcol)).alias(
                "SpeedLimitPositions"
            ),
            speedlimitcol,
            "XPos",
            "DatTime",
        ]
    )

    block_marks = speedlimitpos.filter(pl.col("SpeedLimitPositions"))
    drivedata.data = drivedata.data.with_columns(
        pl.lit(None).cast(pl.Int32).alias("SpeedLimitBlocks")
    )

    mph2mps = 0.44704

    blocknumber = 1
    for row in block_marks.rows(named=True):
        drivedata.data = drivedata.data.with_columns(
            pl.when(
                pl.col("DatTime")
                .cast(pl.Float32)
                .is_between(row["DatTime"] - 5, row["DatTime"] + 5)
            )
            .then(blocknumber)
            .otherwise(pl.col("SpeedLimitBlocks"))
            .alias("SpeedLimitBlocks")
        )
        blocknumber += 1

    return drivedata


@registerFilter()
def writeToCSV(
    drivedata: pydre.core.DriveData, outputDirectory: str
) -> pydre.core.DriveData:
    sourcefilename = Path(drivedata.sourcefilename).stem
    outputfilename = Path(outputDirectory).with_stem(sourcefilename).with_suffix(".csv")
    drivedata.data.write_csv(outputfilename)
    return drivedata


def filetimeToDatetime(ft: int) -> Optional[datetime.datetime]:
    EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as filetime
    HUNDREDS_OF_NS = 10000000
    s, ns100 = divmod(ft - EPOCH_AS_FILETIME, HUNDREDS_OF_NS)
    try:
        result = datetime.datetime.fromtimestamp(s, tz=datetime.timezone.utc).replace(
            microsecond=(ns100 // 10)
        )
    except OSError:
        # happens when the input to fromtimestamp is outside the legal range
        result = None
    return result


def mergeSplitFiletime(hi: int, lo: int):
    return struct.unpack("Q", struct.pack("LL", lo, hi))[0]

@registerFilter()
def removeOddData(drivedata: pydre.core.DriveData, col: str, lower: int, upper: int) -> pydre.core.DriveData:
    """
    Params:
    col: The name of the column to filter data
    lower: lower bound to filter
    upper: upper bound to filter
    """
    """
    Removes data in a certain range for a certain variable. 
    """
    required_col = [col]
    drivedata.checkColumns(required_col)

    new_dd = drivedata.data.with_columns(
        (pl.col(col).clip(lower_bound=lower)).alias(col))

    return
