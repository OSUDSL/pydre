import polars as pl
from pandas import DataFrame
import csv
import datetime
import glob
import os
import pathlib
import threading
import numpy as np
from fastavro import reader as avroreader

from ..core import DriveData, ColumnsMatchError
from . import registerFilter

from typing import Optional, Any

import neurokit2 as nk
from loguru import logger

# Serialises all overlap-report writes across threads spawned by ThreadPoolExecutor.
_overlap_report_lock = threading.Lock()

_OVERLAP_REPORT_FIELDS = [
    "participant_id",
    "roi",
    "avro_file",
    "field",
    "status",
    "empatica_start",
    "empatica_stop",
    "dat_start",
    "dat_stop",
    "overlap_start",
    "overlap_stop",
]


def _write_overlap_report(report_path: str, row: dict) -> None:
    """Append one overlap row to *report_path* in a thread-safe manner.

    The CSV header is written automatically the first time the file is created.
    All subsequent calls append rows without repeating the header.
    """
    with _overlap_report_lock:
        exists = pathlib.Path(report_path).exists()
        with open(report_path, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_OVERLAP_REPORT_FIELDS)
            if not exists:
                writer.writeheader()
            writer.writerow(row)


def _ts_us_to_iso(ts_us: int) -> str:
    """Convert a Unix microsecond timestamp to an ISO 8601 string (UTC)."""
    return datetime.datetime.fromtimestamp(
        ts_us / 1e6, tz=datetime.timezone.utc
    ).isoformat()


import pydre.core
from pydre.filters import registerFilter

THISDIR = pathlib.Path(__file__).resolve().parent


# Reads and stores all participant information and data in records.
def getRecords(avroPath):
    with open(avroPath, "rb") as f:
        # reader = DataFileReader(f, DatumReader())
        records = [r for r in avroreader(f)]
        # reader.close()
    return records


# Returns the start and stop times of avro file for eda, temp, and bvp.
# Prints the participant ID, start and stop times of avro file for eda, temp, and bvp.
# Print statements are commented out.
def find_raw_time_extents(avroPath: str) -> tuple[list[datetime.datetime], list[datetime.datetime]]:
    # Get the participant info & data from getRecords() and store in avro_records.
    avro_records = getRecords(avroPath)

    # Iterate through the 3 raw data fields to print each of their start and stop times.
    rawDataFieldNames = ["eda", "temperature", "bvp"]
    # startTimes and stopTimes will be returned and used in determining the min and max times.
    startTimes = []
    stopTimes = []
    for fieldName in rawDataFieldNames:
        # Get the start timestamp from avro_records.
        timestampStart = avro_records[0]["rawData"][fieldName]["timestampStart"]
        # avro timestamp is in microseconds
        avroStart = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
            microseconds=timestampStart
        )
        # Add each start time to startTimes.
        startTimes.append(avroStart)

        # Get the sampling frequency and number of recorded data points from avro_records.
        # Stop time formula: start time + ((1 / sampling frequency) * # data points)
        sampFreq = avro_records[0]["rawData"][fieldName]["samplingFrequency"]
        sampFreq = 1 / sampFreq
        numValues = len(avro_records[0]["rawData"][fieldName]["values"])
        avroStop = avroStart + datetime.timedelta(seconds=sampFreq * numValues)
        stopTimes.append(avroStop)
    # Return the times as a tuple.
    return startTimes, stopTimes


# Returns the minimum start time and the maximum stop time of the 3 raw data fields.
def find_time_extents(av_file: str) -> tuple[datetime.datetime, datetime.datetime]:
    # Get all of the start and stop times from showTime.
    starts, stops = find_raw_time_extents(av_file)
    starts.sort()
    stops.sort()
    # return minimum start time, maximum stop time
    return starts[0], stops[-1]


def get_dataframe_of_field(avro, data_field):
    avroMetricVals = avro["rawData"][data_field]["values"]
    # generate timestamps of AVRO data
    avroStartTimestamp = avro["rawData"][data_field]["timestampStart"]
    avroSamplingFreq = avro["rawData"][data_field]["samplingFrequency"]
    if avroSamplingFreq == 0:
        logger.warning("Zero sampling frequency in avro file")
        return None, 0

    avroTimestamps = [
        round(avroStartTimestamp + i * (1e6 / avroSamplingFreq))
        for i in range(len(avroMetricVals))
    ]
    avroFieldData = pl.DataFrame(
        {"rawtimestamp": avroTimestamps, data_field: avroMetricVals}
    )
    avroFieldData = avroFieldData.with_columns(
        pl.col("rawtimestamp").cast(pl.Datetime(time_unit="us")).alias("datetime")
    )
    return avroFieldData, avroSamplingFreq


@registerFilter()
def MergeEmpaticaData(
    drivedata: DriveData,
    lookup_csv: str,
    avro_dir: str,
    target_fields: list[str] = ["eda", "temperature", "bvp"],
    overlap_report: Optional[str] = None,
):
    """
    Reads the lookup csv, finds EmpaticaID for this ParticipantID,
    reads the matching .avro file from avro_dir, and merges each field into drivedata.data.



    """
    # 1. load lookup and filter

    lookup = pl.read_csv(source=lookup_csv)
    pid = drivedata.metadata["ParticipantID"]
    row = lookup.filter(pl.col("ParticipantID") == int(pid))
    if row.is_empty():
        logger.warning(f"No Empatica mapping for ParticipantID {pid}")
        return drivedata

    # 2. build avro path and find all avro files matching participantID
    emp_id = row["EmpaticaID"][0]

    """
    # look through avro_dir and return list of filenames with emp_id matching participantID
    avro_filelist = os.listdir(avro_dir)

    # considering all avro files, filtering out those that do not match this participant
    afname = f"1-1-{emp_id}*.avro" # the avro filename pattern for this participant, with prefix and wildcard
    afpath = pathlib.Path(avro_dir).joinpath(afname) # the full path to files with this pattern to be passed into glob
    matching_avro_files = glob.glob(str(afpath))  # the string list of all files with full paths for this participant

    logger.info(f"Found {len(matching_avro_files)} avro files for Participant {pid} with EmpaticaID {emp_id}")

    # ensure that all of these paths are valid
    for f in matching_avro_files:
        if not pathlib.Path(f).exists():
            logger.warning(f"Missing avro file {f}")
            return drivedata
    """

    # Build a glob pattern that searches recursively under avro_dir
    # '**' matches any number of nested subdirectories
    pattern = os.path.join(avro_dir, "**", f"1-1-{emp_id}_*.avro")

    # Execute the glob search with recursive=True to traverse all subfolders
    matching_avro_files = glob.glob(pattern, recursive=True)

    # If no .avro files are found for this participant, log a warning and exit early
    if not matching_avro_files:
        logger.warning(
            f"No avro files found for ParticipantID {pid}"
        )  # warn about missing data
        return drivedata  # return the original data without modification

    # 3. prepare dat dataframe
    dat = drivedata.data

    # 3a. ensure wallTimestamp is present (if not already)
    if "wallTimestamp" not in dat.columns:
        dat = (
            dat.with_columns(
                (
                    np.bitwise_or(
                        np.left_shift(pl.col("hiFileTime"), 32), pl.col("lowFileTime")
                    )
                    / 10
                ).alias("fileTimeMicroSecs")
            )
            .with_columns(
                (
                    pl.datetime(1601, 1, 1, time_zone="UTC")
                    + pl.duration(microseconds=pl.col("fileTimeMicroSecs"))
                ).alias("wallTime")
            )
            .with_columns(
                pl.col("wallTime").dt.timestamp(time_unit="us").alias("wallTimestamp")
            )
            .drop(["fileTimeMicroSecs", "wallTime"])
        )

    # 3b. init biometric cols
    for f in target_fields:
        if f not in dat.columns:
            dat = dat.with_columns(pl.lit(None).cast(pl.Float32).alias(f))

    dat_min = dat["wallTimestamp"].min()
    dat_max = dat["wallTimestamp"].max()

    # need to consider multiple avro files for each participant. better to combine avro files before doing this or loop through them individually?
    dd_appended = drivedata.data  # how to append to a dataframe in this context?
    for m in matching_avro_files:
        avro_path = pathlib.Path(m)
        # 4. read avro record
        with open(avro_path, "rb") as f:
            avro = [r for r in avroreader(f)][0]
        logger.info(f"Merging {avro_path.name} into Participant {pid}")

        # 5. interpolate each field
        for f in target_fields:
            # avro_field, _ = avroutils.get_dataframe_of_field(avro, f)
            avro_field, _ = get_dataframe_of_field(avro, f)  # cgw 06252025
            if avro_field is None:
                # error, abort
                logger.warning(f"Could not retrieve field {f} from {avro_path.name}")
                return drivedata

            # Capture full avro extent BEFORE filtering so we always have it for the report
            avro_raw_min = avro_field["rawtimestamp"].min()
            avro_raw_max = avro_field["rawtimestamp"].max()

            # filter to overlap avro file
            avro_field = avro_field.filter(
                (pl.col("rawtimestamp") >= dat_min)
                & (pl.col("rawtimestamp") <= dat_max)
            )

            # Human-readable time strings – cheap to compute, used by both the report and
            # the logger.warning fallback, so always compute them unconditionally.
            empatica_start_hr = _ts_us_to_iso(avro_raw_min)
            empatica_stop_hr  = _ts_us_to_iso(avro_raw_max)
            dat_start_hr      = _ts_us_to_iso(dat_min)
            dat_stop_hr       = _ts_us_to_iso(dat_max)

            if avro_field.is_empty():
                logger.warning(
                    f"No overlap on {f} for Part. {pid}, ROI {drivedata.roi} in {avro_path.name}"
                )
                if overlap_report:
                    _write_overlap_report(
                        overlap_report,
                        {
                            "participant_id": pid,
                            "roi": drivedata.roi,
                            "avro_file": avro_path.name,
                            "field": f,
                            "status": "no_overlap",
                            "empatica_start": empatica_start_hr,
                            "empatica_stop": empatica_stop_hr,
                            "dat_start": dat_start_hr,
                            "dat_stop": dat_stop_hr,
                            "overlap_start": "",
                            "overlap_stop": "",
                        },
                    )
                else:
                    logger.warning(
                        f"  Avro '{f}' time range : {empatica_start_hr} → {empatica_stop_hr}"
                    )
                    logger.warning(
                        f"  Drive data time range : {dat_start_hr} → {dat_stop_hr}"
                    )
                continue

            # Overlap exists – record the actual overlap window
            if overlap_report:
                overlap_min = avro_field["rawtimestamp"].min()
                overlap_max = avro_field["rawtimestamp"].max()
                _write_overlap_report(
                    overlap_report,
                    {
                        "participant_id": pid,
                        "roi": drivedata.roi,
                        "avro_file": avro_path.name,
                        "field": f,
                        "status": "overlap",
                        "empatica_start": empatica_start_hr,
                        "empatica_stop": empatica_stop_hr,
                        "dat_start": dat_start_hr,
                        "dat_stop": dat_stop_hr,
                        "overlap_start": _ts_us_to_iso(overlap_min),
                        "overlap_stop":  _ts_us_to_iso(overlap_max),
                    },
                )

            dat_sub = dat.filter(
                (pl.col("wallTimestamp") >= avro_field["rawtimestamp"].min())
                & (pl.col("wallTimestamp") <= avro_field["rawtimestamp"].max())
            ).drop(f)

            if f == "eda":
                signals, info = processRawEDA(avro_field, 4)
                signals_pl = pl.DataFrame(
                    signals
                )  # doesn't include timestamps, have to add them back
                signals_pl = signals_pl.with_columns(
                    pl.Series("rawtimestamp", avro_field["rawtimestamp"])
                )

                binary_cols = ["SCR_Peaks", "SCR_Onsets", "SCR_Recovery"]
                continuous_cols = ["EDA_Clean", "EDA_Tonic", "EDA_Phasic"]
                processed_edacols = []

                for col in signals_pl.columns:
                    # logger.info(f"Processing column {col} for {pid}")
                    if col in continuous_cols:
                        # logger.info(f"Processing continuous column {col} for {pid}")
                        resampled_vals = np.interp(
                            dat_sub["wallTimestamp"].to_numpy(),
                            signals_pl["rawtimestamp"].to_numpy(),
                            signals_pl[col].to_numpy(),
                        )
                        processed_edacols.append(pl.Series(col, resampled_vals))

                    elif col in binary_cols:
                        # logger.info(f"Processing binary column {col} for {pid}")
                        dat_timestamps = dat_sub["wallTimestamp"].to_numpy()

                        signal_only_ones = signals_pl.select(
                            "rawtimestamp", col
                        ).filter(pl.col(col) == 1)

                        signal_timestamps = signal_only_ones["rawtimestamp"].to_numpy()

                        signal_vals = signal_only_ones[col].to_numpy()

                        # logger.info(f"{col} signal_vals sum: {np.sum(signal_vals)}")

                        nearestTime = np.searchsorted(signal_timestamps, dat_timestamps)
                        clipped = np.clip(nearestTime, 0, len(signal_timestamps) - 1)
                        prev = np.clip(nearestTime - 1, 0, len(signal_timestamps) - 1)

                        diff_clipped = np.abs(
                            signal_timestamps[clipped] - dat_timestamps
                        )
                        diff_prev = np.abs(signal_timestamps[prev] - dat_timestamps)

                        closer_times = np.where(diff_clipped < diff_prev, clipped, prev)
                        tolerance = np.minimum(diff_clipped, diff_prev)

                        resampled_avro_vals = np.zeros_like(dat_timestamps)
                        resampled_avro_vals[np.unique(closer_times)] = 1

                        # logger.info(f"{col} resampled_vals sum: {np.sum(resampled_avro_vals)}")

                        # new approach
                        # resampled_avro_vals = np.zeros_like(dat_timestamps)
                        # for peak in signal_timestamps:
                        # index = np.argmin(np.abs(dat_timestamps - peak))
                        # resampled_avro_vals[index] = 1

                        processed_edacols.append(pl.Series(col, resampled_avro_vals))

                allEDACols = continuous_cols + binary_cols
                allEDACols.append("wallTimestamp")
                dat_sub = (
                    dat_sub.select(pl.all().exclude(continuous_cols + binary_cols))
                    .hstack(processed_edacols)
                    .select(allEDACols)
                )
                # logger.info(f'Before merge, SCR_Peaks sum: {dat_sub.select(pl.col("SCR_Peaks")).sum().item()}')
                merged = dat.join_asof(
                    dat_sub, on="wallTimestamp", tolerance=10, coalesce=True
                )
                # logger.info(f'After merge, SCR_Peaks sum: {merged.select(pl.col("SCR_Peaks")).sum().item()}')
                # coalesce all the EDA columns to make sure we're not overwriting data
                # logger.info(f"Columns in merged: {merged.columns}")
                for col in allEDACols:
                    col_right = f"{col}_right"
                    if col_right in merged.columns:
                        # logger.info(f"Merging column {col} with {col_right} for Participant {pid}")
                        merged = merged.with_columns(
                            pl.coalesce(pl.col(col), pl.col(f"{col}_right")).alias(col)
                        ).drop(f"{col}_right")
                dat = merged
                # logger.info(f"Columns in dat: {dat.columns}")

            else:
                resampled_avro_vals = np.interp(
                    dat_sub["wallTimestamp"].to_numpy(),
                    avro_field["rawtimestamp"].to_numpy(),
                    avro_field[f].to_numpy(),
                )
                dat_sub = dat_sub.hstack([pl.Series(f, resampled_avro_vals)]).select(
                    "wallTimestamp", f
                )
                # logger.info(f"Columns in dat_sub: {dat_sub.columns}")
                dat = dat.join_asof(
                    dat_sub, on="wallTimestamp", tolerance=10, coalesce=True
                )
                # merge column f and f_right
                dat = dat.with_columns(
                    pl.coalesce(pl.col(f), pl.col(f"{f}_right")).alias(f)
                ).drop(f"{f}_right")

    # logger.info(f"After merge, means of fields for Participant {pid}:")
    # for f in target_fields:
    #    logger.info(f"\tmean({f}) = {dat[f].mean()}")

    drivedata.data = dat
    return drivedata


@registerFilter()
def MergeEmpaticaBiomarkers(
    drivedata: DriveData,
    lookup_csv: str,
    biomarker_dir: str,
    target_fields: list[str] = ["prv", "pulse-rate", "respiratory-rate"],
    overlap_report: Optional[str] = None,
) -> pydre.core.DriveData:
    """
    Merge Empatica biomarker CSV files into the DriveData object.

    Steps:
    1. Load the participant-to-EmpaticaID mapping.
    2. Find all matching biomarker CSVs recursively under biomarker_dir.
    3. Ensure drivedata.data has a wallTimestamp column.
    4. Initialize target fields in the data if missing.
    5. For each CSV:
       a. Read CSV and convert timestamp_unix to rawtimestamp (µs).
       b. Filter biomarker rows to overlap drivedata time bounds.
       c. Interpolate each target field onto wallTimestamp grid.
       d. Merge interpolated values back into main DataFrame.
    6. Assign updated DataFrame back to drivedata.data.
    """

    # 1. Read lookup CSV to map ParticipantID to EmpaticaID
    lookup_df = pl.read_csv(lookup_csv)
    pid = int(drivedata.metadata.get("ParticipantID", -1))
    mapping = lookup_df.filter(pl.col("ParticipantID") == pid)
    if mapping.is_empty():
        logger.warning(f"No EmpaticaID found for ParticipantID {pid}")
        return drivedata
    emp_id = mapping.select("EmpaticaID").to_series()[0]

    # 2. Discover biomarker CSV files under biomarker_dir (recursively)
    pattern = os.path.join(biomarker_dir, "**", f"*{emp_id}_*.csv")
    csv_paths = glob.glob(pattern, recursive=True)
    if not csv_paths:
        logger.warning(
            f"No biomarker CSVs found for Participant {pid}, EmpaticaID {emp_id}"
        )
        return drivedata

    # 3. Prepare the main data DataFrame and ensure wallTimestamp exists
    dat = drivedata.data
    if "wallTimestamp" not in dat.columns:
        file_time = drivedata.metadata.get("fileTimeMicroSecs")
        if file_time is None:
            logger.warning(
                "Cannot find fileTimeMicroSecs in metadata, abort Empatica merge"
            )
            return drivedata
        start_ts = datetime.datetime.fromtimestamp(file_time / 1e6, tz=datetime.timezone.utc)
        dat = dat.with_columns(
            (pl.lit(start_ts) + pl.col("timestamp").cast(pl.Duration("us"))).alias(
                "wallTimestamp"
            )
        )
        # convert to integer µs for consistent joins
        dat = dat.with_columns(
            pl.col("wallTimestamp").cast(pl.Int64).alias("wallTimestamp")
        )

    # sort once for asof joins
    dat = dat.sort("wallTimestamp")

    # Determine overall time bounds of the drive data as Python scalars (µs)
    dat_min = int(dat["wallTimestamp"].min())
    dat_max = int(dat["wallTimestamp"].max())

    filtered_csv_paths = [
        s for s in csv_paths if any(sub in s for sub in target_fields)
    ]

    # 5. Process each biomarker CSV
    for csv_path in filtered_csv_paths:
        # a. Read CSV and convert timestamp_unix (ms) → rawtimestamp (µs int)
        bio_df = pl.read_csv(csv_path)
        bio_df = bio_df.with_columns(
            (pl.col("timestamp_unix") * 1_000).cast(pl.Int64).alias("rawtimestamp")
        )

        field_to_extract = bio_df.columns[3]
        if field_to_extract not in dat.columns:
            dat = dat.with_columns(
                pl.lit(None).cast(pl.Float32).alias(field_to_extract)
            )

        # Capture full biomarker CSV extent BEFORE filtering so we always have it for the report
        bio_raw_min = int(bio_df["rawtimestamp"].min())
        bio_raw_max = int(bio_df["rawtimestamp"].max())

        # b. Filter to overlapping time range using integer bounds
        bio_df = bio_df.filter(
            (pl.col("rawtimestamp") >= dat_min) & (pl.col("rawtimestamp") <= dat_max)
        )

        # Human-readable time strings for logging and reporting
        empatica_start_hr = _ts_us_to_iso(bio_raw_min)
        empatica_stop_hr  = _ts_us_to_iso(bio_raw_max)
        dat_start_hr      = _ts_us_to_iso(dat_min)
        dat_stop_hr       = _ts_us_to_iso(dat_max)

        if bio_df.is_empty():
            if overlap_report:
                _write_overlap_report(
                    overlap_report,
                    {
                        "participant_id": pid,
                        "roi": drivedata.roi,
                        "avro_file": os.path.basename(csv_path),
                        "field": field_to_extract,
                        "status": "no_overlap",
                        "empatica_start": empatica_start_hr,
                        "empatica_stop": empatica_stop_hr,
                        "dat_start": dat_start_hr,
                        "dat_stop": dat_stop_hr,
                        "overlap_start": "",
                        "overlap_stop": "",
                    },
                )
            else:
                logger.warning(
                    f"No overlapping biomarkers for Participant {pid} ({emp_id}) in {os.path.basename(csv_path)}"
                )
                logger.warning(
                    f"  CSV '{os.path.basename(csv_path)}' time range : {empatica_start_hr} → {empatica_stop_hr}"
                )
                logger.warning(
                    f"  Drive data time range : {dat_start_hr} → {dat_stop_hr}"
                )
            continue

        # Overlap exists – record the actual overlap window
        if overlap_report:
            overlap_min = int(bio_df["rawtimestamp"].min())
            overlap_max = int(bio_df["rawtimestamp"].max())
            _write_overlap_report(
                overlap_report,
                {
                    "participant_id": pid,
                    "roi": drivedata.roi,
                    "avro_file": os.path.basename(csv_path),
                    "field": field_to_extract,
                    "status": "overlap",
                    "empatica_start": empatica_start_hr,
                    "empatica_stop": empatica_stop_hr,
                    "dat_start": dat_start_hr,
                    "dat_stop": dat_stop_hr,
                    "overlap_start": _ts_us_to_iso(overlap_min),
                    "overlap_stop":  _ts_us_to_iso(overlap_max),
                },
            )

        # Prepare numpy arrays for interpolation (µs)
        times_num = bio_df["rawtimestamp"].to_numpy().astype("int64")

        # c. Interpolate each target field

        field = field_to_extract

        if field not in bio_df.columns:
            logger.warning(f"Missing field '{field}' in {os.path.basename(csv_path)}")
            continue
        # cast values via numpy instead of passing dtype to to_numpy()
        raw_vals = bio_df[field].to_numpy()
        values = raw_vals.astype(np.float32)

        # select segment of dat within this CSV's time window
        time_start = int(times_num.min())
        time_end = int(times_num.max())
        sub_df = dat.filter(pl.col("wallTimestamp").is_between(time_start, time_end))
        sub_ts = sub_df["wallTimestamp"].to_numpy().astype("int64")

        # perform linear interpolation
        interp_vals = np.interp(sub_ts, times_num, values)

        # d. Create and sort DataFrame for the interpolated segment
        interp_df = pl.DataFrame({"wallTimestamp": sub_ts, field: interp_vals}).sort(
            "wallTimestamp"
        )

        # asof join on integer µs with 1-second tolerance ← 1e6 µs
        dat = (
            dat.join_asof(
                interp_df,
                on="wallTimestamp",
                tolerance=1_000_000,  # 1 second in microseconds
                strategy="forward",
            )
            .with_columns(
                pl.when(pl.col(field).is_null())
                .then(pl.col(f"{field}_right"))
                .otherwise(pl.col(field))
                .alias(field)
            )
            .drop(f"{field}_right")
        )

    # 6. Assign updated DataFrame back to drivedata and return
    drivedata.data = dat
    return drivedata


def processRawEDA(edadata: DataFrame, sampling_rate: int):
    """
    Processes the raw EDA data from the newly formed drivedata object, adds another column with processed EDA
    """
    dat = edadata
    # verify that eda column is present in drivedata
    # if "eda" not in dat.columns:

    eda_col = dat["eda"]

    # the sampling rate of the empatica embrace plus for eda is... 4 Hz. but we already interpolated it to 60 hz, so we will use 60 hz
    signals, info = nk.eda_process(eda_col, sampling_rate)

    return signals, info
