import re

import polars as pl
from loguru import logger

import pydre.core
from pydre.filters import registerFilter


@registerFilter()
def modifyCriticalEventsCol(drivedata: pydre.core.DriveData):
    ident = drivedata.PartID
    ident_groups = re.match(r"(\d)(\d)(\d)(\d\d\d\d)[wW](\d)", ident)
    if ident_groups is None:
        logger.warning("Could not parse R2D ID " + ident)
        return [None]
    week = ident_groups.group(5)
    scenario = drivedata.scenarioName
    if week == "1" and scenario == "Load, Event":
        # between the x positions, change the critical event status to 1
        drivedata.data = drivedata.data.with_columns(
            pl.when(2165 < pl.col("XPos"), pl.col("XPos") < 2240)
            .then(1)
            .when(pl.col("CriticalEventStatus") == 1)
            .then(1)
            .otherwise(0)
            .alias("CriticalEventStatus")
        )
    return drivedata


@registerFilter()
def modifyUABdata(drivedata: pydre.core, headwaycutoff=50):
    ident = drivedata.PartID
    ident_groups = re.match(r"(\d)(\d)(\d)(\d\d\d\d)[wW](\d)", ident)
    if ident_groups is None:
        logger.warning("Could not parse R2D ID " + ident)
        return [None]
    location = ident_groups.group(2)
    df = drivedata.data
    if location == "1":
        # copy values from datTime into simTime
        df = df.with_columns(pl.col("DatTime").alias("SimTime"))
        # for files like Experimenter_3110007w1_No Load, Event_1665239271T-10-07-52.dat where the drive starts at
        # the end of a previous drive, trim the data leading up to the actual start
        df = df.with_columns(
            pl.col("XPos").cast(pl.Float32).diff().abs().alias("PosDiff")
        )
        df_actual_start = df.filter(df.get_column("PosDiff") > 500)
        if not df_actual_start.is_empty():
            start_time = df_actual_start.get_column("SimTime").item(0)
            df = df.filter(df.get_column("SimTime") > start_time)
        # modify xpos to match the starting value of dsl data
        start_pos = df.get_column("XPos").item(0)
        # add critical event status based on scenario type
        scenario = drivedata.scenarioName
        if scenario == "Load, Event":
            cutoff_df = df.filter(df.get_column("XPos") > (4350 + start_pos))
            try:
                start_cutoff = (
                    cutoff_df.filter(
                        cutoff_df.get_column("HeadwayDistance") < headwaycutoff
                    )
                    .get_column("XPos")
                    .item(0)
                ) + 135
                df = df.with_columns(
                    pl.when(
                        pl.col("XPos") > start_pos + 2155,
                        pl.col("XPos") < start_pos + 2239.5,
                    )
                    .then(1)
                    .when(
                        pl.col("XPos") > start_cutoff, pl.col("XPos") < start_pos + 4720
                    )
                    .then(1)
                    .when(
                        pl.col("XPos") > start_pos + 6191.4,
                        pl.col("XPos") < start_pos + 6242,
                    )
                    .then(1)
                    .otherwise(0)
                    .alias("CriticalEventStatus")
                )
            except IndexError:
                df = df.with_columns(
                    pl.when(
                        pl.col("XPos") > start_pos + 2155,
                        pl.col("XPos") < start_pos + 2239.5,
                    )
                    .then(1)
                    .when(
                        pl.col("XPos") > start_pos + 6191.4,
                        pl.col("XPos") < start_pos + 6242,
                    )
                    .then(1)
                    .otherwise(0)
                    .alias("CriticalEventStatus")
                )
        else:
            cutoff_df = df.filter(df.get_column("XPos") > (4550 + start_pos))
            try:
                start_cutoff = (
                    cutoff_df.filter(
                        cutoff_df.get_column("HeadwayDistance") < headwaycutoff
                    )
                    .get_column("XPos")
                    .item(0)
                ) + 135
                df = df.with_columns(
                    pl.when(
                        pl.col("XPos") > (start_pos + 1726),
                        pl.col("XPos") < (start_pos + 1790),
                    )
                    .then(1)
                    .when(
                        pl.col("XPos") > (start_pos + 3222),
                        pl.col("XPos") < (start_pos + 3300),
                    )
                    .then(1)
                    .when(
                        pl.col("XPos") > start_cutoff,
                        pl.col("XPos") < (start_pos + 5500),
                    )
                    .then(1)
                    .otherwise(0)
                    .alias("CriticalEventStatus")
                )
            except IndexError:
                df.with_columns(
                    pl.when(
                        pl.col("XPos") > (start_pos + 1726),
                        pl.col("XPos") < (start_pos + 1790),
                    )
                    .then(1)
                    .when(
                        pl.col("XPos") > (start_pos + 3222),
                        pl.col("XPos") < (start_pos + 3300),
                    )
                    .then(1)
                    .otherwise(0)
                    .alias("CriticalEventStatus")
                )
    drivedata.data = df
    return drivedata
