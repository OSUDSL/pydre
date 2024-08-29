import datetime
import struct
from loguru import logger
from pathlib import Path
import polars as pl
import pydre.core
from . import registerFilter


@registerFilter()
def numberBinaryBlocks(
    drivedata: pydre.core.DriveData,
    binary_column="ButtonStatus",
    new_column="NumberedBlocks",
    only_on=0,
    fill_after_block=0,
    extend_blocks=0,
):

    required_col = [binary_column]
    diff = drivedata.checkColumns(required_col)

    blocks = drivedata.data.select(
        (pl.col(binary_column).shift() != pl.col(binary_column))
        .cum_sum()
        .alias(new_column)
    )

    drivedata.data.hstack(blocks, in_place=True)
    if only_on:
        try:
            drivedata.data = drivedata.data.filter(pl.col(binary_column) == 1)
        except pl.exceptions.ComputeError as e:
            logger.warning(
                "Assumed binary column {} in {} has non-numeric value.".format(
                    binary_column, drivedata.sourcefilename
                )
            )

    if extend_blocks:
        drivedata.data = drivedata.data.with_columns(
            pl.when(pl.col(binary_column) == 0).then(None).otherwise(pl.col(new_column)).alias(new_column)
        )
        drivedata.data = drivedata.data.with_columns(pl.col(new_column).fill_null(strategy="forward"))
        drivedata.data = drivedata.data.filter(pl.col(new_column).is_not_null())

    return drivedata


@registerFilter()
def SimTimeFromDatTime(drivedata: pydre.core.DriveData):
    drivedata.data = drivedata.data.with_columns(pl.col("DatTime").alias("SimTime"))
    return drivedata


@registerFilter()
def FixReversedRoadLinearLand(drivedata: pydre.core.DriveData):
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
):
    drivedata.data = drivedata.data.with_columns(
        pl.when(pl.col(colforrange).cast(pl.Float32).is_between(rangemin, rangemax))
        .then(valtoset)
        .otherwise(pl.col(coltoset))
        .cast(pl.Float32)
        .alias(coltoset)
    )

    return drivedata


@registerFilter()
def relativeBoxPos(drivedata: pydre.core.DriveData):
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
def zscoreCol(drivedata: pydre.core.DriveData, col: str, newcol: str):
    colMean = drivedata.data.get_column(col).mean()
    colSD = drivedata.data.get_column(col).std()
    drivedata.data = drivedata.data.with_columns(
        ((pl.col(col) - colMean) / colSD).alias(newcol)
    )
    return drivedata

@registerFilter()
def speedLimitTransitionMarker(drivedata: pydre.core.DriveData, speedlimitcol: str):
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
def writeToCSV(drivedata: pydre.core.DriveData, outputDirectory: str):
    sourcefilename = Path(drivedata.sourcefilename).stem
    outputfilename = Path(outputDirectory).with_stem(sourcefilename).with_suffix(".csv")
    drivedata.data.write_csv(outputfilename)
    return drivedata


@registerFilter()
def filetimeToDatetime(ft: int):
    EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as filetime
    HUNDREDS_OF_NS = 10000000
    s, ns100 = divmod(ft - EPOCH_AS_FILETIME, HUNDREDS_OF_NS)
    try:
        result = datetime.datetime.fromtimestamp(s, tz=datetime.timezone.utc).replace(
            microsecond=(ns100 // 10)
        )
    except OSError:
        # happens when the input to fromtimestamp is outside of the legal range
        result = None
    return result


def mergeSplitFiletime(hi: int, lo: int):
    return struct.unpack("Q", struct.pack("LL", lo, hi))[0]


