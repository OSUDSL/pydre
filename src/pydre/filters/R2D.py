import re
import pathlib

import polars as pl
from loguru import logger

import pydre.core
from pydre.filters import registerFilter

THISDIR = pathlib.Path(__file__).resolve().parent


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
def CropStartPosition(drivedata: pydre.core):
    """
    Ensure that drive data starts from consistent point between sites.
    This code was decoupled from merge filter to zero UAB start points.
    """
    df = drivedata.data
    # copy values from datTime into simTime
    df = df.with_columns(pl.col("DatTime").alias("SimTime"))
    df = df.with_columns(
        pl.col("XPos").cast(pl.Float32).diff().abs().alias("PosDiff")
    )
    df_actual_start = df.filter(df.get_column("PosDiff") > 500)
    if not df_actual_start.is_empty():
        start_time = df_actual_start.get_column("SimTime").item(0)
        df = df.filter(df.get_column("SimTime") > start_time)

    drivedata.data = df
    return drivedata


@registerFilter()
def MergeCriticalEventPositions(drivedata: pydre.core,
                                dataFile="",
                                analyzePriorCutOff=False,
                                criticalEventDist=250.0,
                                cutOffDist=150.0,
                                cutInDist=50.0,
                                cutInStart=200.0,
                                cutOffStart=200.0,
                                cutInDelta=2.5,
                                headwayThreshold=250.0):
    """
    :arg: dataFile: the file name of the csv that maps CE positions.
        -> required cols:
        'Week','ScenarioName','Event','maneuver pos','CENum'
    :arg: analyzePriorCutIn: True: analyze Subject's reaction before cut-In CE
                            False: analyze Subject's reaction after cut-In CE
    :arg: criticalEventDist: determines how many meters on the X-axis
        is determined to be "within the critical event duration"
    :arg: cutOffDist: distance modifier in meters for cut-off range
    :arg: cutInDist: distance modifier in meters for cut-in range
    :arg: cutInStart: offset for cut-in event execution start
    :arg: cutOffStart: offset for cut-off event execution start
    :arg: cutInDelta: time, in seconds, to account for subject
        reaction inclusion to ROI for Cut-Off Critical Event.

    with defaults:
    cut-in: range=300m; start_offset=200
    cut-off: range=400m; start_offset=200
    trashtip: range=250m; start_offset=0

    Imports specified csv dataFile for use in XPos-based filtering,
    using 'manuever pos'. dataFile also determines additional columns
    in the filtered result:
        - CriticalEventNum
        - EventName
    """
    ident = drivedata.PartID
    scenario = drivedata.scenarioName
    # (control=5/case=3)(UAB=1/OSU=2)(Male=1/Female=2)(R2D_ID)w(Week Num)
    ident_groups = re.match(r"(\d)(\d)(\d)(\d\d\d\d)[wW](\d)", ident)
    if ident_groups is None:
        logger.warning("Could not parse R2D ID " + ident)
        return [None]
    week = ident_groups.group(5)
    df = drivedata.data

    if "No Event" not in scenario:
        # adding cols with meaningless values for later CE info, ensuring shape
        df = df.with_columns(
            pl.lit(-1).alias("CriticalEventNum"),
            pl.lit("").alias("EventName")
        )
        if dataFile != "":
            merge_df = pl.read_csv(source=dataFile)
            merge_df = merge_df.filter(
                    merge_df.get_column("ScenarioName") == scenario,
                    merge_df.get_column("Week") == week
            )
        else:
            raise Exception("Datafile not present - cannot merge w/o source of truth.")

        ceInfo_df = merge_df.select(
            pl.col("manuever pos"),
            pl.col("CENum"),
            pl.col("Event")
            )
        filter_df = df.clear()

        for ceRow in ceInfo_df.rows():
            # critical event position, number, and name
            cePos = ceRow[0]
            ceNum = ceRow[1]
            event = ceRow[2]

            # Activation vs manuever execution dictates need for range adjust
            if "cut-in" in event.lower():
                criticalEventDist += cutInDist
                cePos += cutInStart
            elif "cut-off" in event.lower():
                criticalEventDist += cutOffDist
                cePos += cutOffStart

            # xPos based bounding, consider
            ceROI = df.filter(
                    df.get_column('XPos') >= cePos,
                    df.get_column('XPos') < cePos + criticalEventDist
                )
            # update existing columns with Critical Event values
            ceROI = ceROI.with_columns(
                pl.lit(ceNum).alias("CriticalEventNum"),
                pl.lit(event).alias("EventName")
            )

            # cut-off/in need better filtering, based on headway check
            if "trash" not in event.lower():
                headwayROI = ceROI.filter(
                    ceROI.get_column('HeadwayDistance') <= headwayThreshold
                )
                if not headwayROI.is_empty():
                    logger.debug(f"{event} recovery detected in data.")
                    # rewind and/or expand timeframe for cut-off timings
                    if "cut-off" in event.lower():
                        simTimeStart = headwayROI.get_column('SimTime').head(1).item()
                        simTimeEnd = headwayROI.get_column('SimTime').tail(1).item()
                        if analyzePriorCutOff:
                            ceROI = df.filter(
                                df.get_column('SimTime') >= simTimeStart - cutInDelta,
                                df.get_column('SimTime') <= simTimeEnd
                            )
                        else:
                            ceROI = df.filter(
                                df.get_column('SimTime') >= simTimeStart,
                                df.get_column('SimTime') <= simTimeEnd + cutInDelta
                            )
                        ceROI = ceROI.with_columns(
                            pl.lit(ceNum).alias("CriticalEventNum"),
                            pl.lit(event).alias("EventName")
                        )
                else:
                    logger.warning(f"{event} Event for {ident} in scenario '{scenario}' does not display expected headway behavior.")

            filter_df.extend(ceROI)
            drivedata.data = filter_df
        if ceInfo_df.shape[0] == 0:
            logger.warning("ERROR! No imported merge info - no known CE positions.")
    else:
        raise Exception("ERROR! Attempting to run 'Event' filtering on scenario with no Events.")
    return drivedata


"""
=================
TODO DEPRECATE:
=================
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
"""
