from loguru import logger
import polars as pl
import pydre.core
from pydre.metrics import registerMetric
import numpy as np
import math
from scipy import signal


# These metrics were used in driving distraction evaluation. They have not been fully tested after conversion from
# Pandas to Polars.


@registerMetric()
def getTaskNum(drivedata: pydre.core.DriveData):
    required_col = ["TaskNum"]
    drivedata.checkColumnsNumeric(required_col)
    taskNum = drivedata.data.get_column("TaskNum").mode()
    if len(taskNum) > 0:
        return taskNum[0]
    else:
        return None


@registerMetric("errorPresses")
def numOfErrorPresses(drivedata: pydre.core.DriveData):
    required_col = ["SimTime", "TaskFail"]
    drivedata.checkColumnsNumeric(required_col)
    df = drivedata.data.select(required_col)
    df = df.unique(maintain_order=True).drop_nulls()
    presses = df.select((pl.col("TaskFail").shift() != pl.col("TaskFail")) > 0).sum()
    return presses


def appendDFToCSV_void(df, csvFilePath: str, sep: str = ","):
    if not os.path.isfile(csvFilePath):
        df.to_csv(csvFilePath, mode="a", index=False, sep=sep)
    elif len(df.columns) != len(pl.read_csv(csvFilePath, nrows=1, sep=sep).columns):
        raise Exception(
            "Columns do not match!! Dataframe has "
            + str(len(df.columns))
            + " columns. CSV file has "
            + str(len(pl.read_csv(csvFilePath, nrows=1, sep=sep).columns))
            + " columns."
        )
    elif not (df.columns == pl.read_csv(csvFilePath, nrows=1, sep=sep).columns).all():
        raise Exception(
            "Columns and column order of dataframe and csv file do not match!!"
        )
    else:
        df.to_csv(csvFilePath, mode="a", index=False, sep=sep, header=False)


@registerMetric(
    columnnames=[
        "numOfGlancesOR",
        "numOfGlancesOR2s",
        "meanGlanceORDuration",
        "sumGlanceORDuration",
    ]
)
def gazeNHTSA(drivedata: pydre.core.DriveData):
    required_col = ["VidTime", "gaze", "gazenum", "TaskFail", "taskblocks", "PartID"]
    drivedata.checkColumns(required_col)

    numofglances = 0

    df = drivedata.data.select(required_col).unique(maintain_order=True).drop_nulls()

    # construct table with columns [glanceduration, glancelocation, error]
    gr = df.group_by("gazenum")

    glancelist = gr.agg(
        durations=(pl.col("VidTime").max() - pl.col("VidTime").min()),
        locations=pl.col("gaze")
        .first()
        .fill_null("offroad")
        .replace(
            ["car.WindScreen", "car.dashPlane", "None"],
            ["onroad", "offroad", "offroad"],
        ),
        error_list=pl.col("TaskFail").any(),
        TaskID=pl.col("TaskID").min(),
        taskblock=pl.col("taskblocks").min(),
        Subject=pl.col("PartID").min(),
    )

    # appendDFToCSV_void(glancelist_aug, "glance_list.csv")

    # table constructed, now find metrics
    # glancelist['over2s'] = glancelist['duration'] > 2

    num_over_2s_offroad_glances = glancelist[
        (glancelist["duration"] > 2) & (glancelist["locations"] == "offroad")
    ]["duration"].count()

    num_offroad_glances = glancelist[(glancelist["locations"] == "offroad")][
        "duration"
    ].count()

    total_time_offroad_glances = glancelist[(glancelist["locations"] == "offroad")][
        "duration"
    ].sum()

    mean_time_offroad_glances = glancelist[(glancelist["locations"] == "offroad")][
        "duration"
    ].mean()

    # print(">2s glances: {}, num glances: {}, total time glances: {}, mean time glances {}".format(
    # num_over_2s_offroad_glances, num_offroad_glances, total_time_offroad_glances, mean_time_offroad_glances))

    return [
        num_offroad_glances,
        num_over_2s_offroad_glances,
        mean_time_offroad_glances,
        total_time_offroad_glances,
    ]


# not working
def addVelocities(drivedata: pydre.core.DriveData):
    df = pl.DataFrame(drivedata.data)
    # add column with ownship velocity
    g = np.gradient(df.XPos.values, df.SimTime.values)
    df.insert(len(df.columns), "OwnshipVelocity", g, True)
    # add column with leadcar velocity
    headwayDist = df.HeadwayTime * df.OwnshipVelocity
    # v = df.OwnshipVelocity+np.gradient(headwayDist, df.SimTime.values)
    df.insert(len(df.columns), "LeadCarPos", headwayDist + df.XPos.values, True)
    df.insert(len(df.columns), "HeadwayDist", headwayDist, True)
    v = np.gradient(headwayDist + df.XPos.values, df.SimTime.values)
    df.insert(len(df.columns), "LeadCarVelocity", v, True)
    return df


@registerMetric()
def crossCorrelate(drivedata: pydre.core.DriveData):
    df = drivedata.data
    if "OwnshipVelocity" not in df.columns or "LeadCarVelocity" not in df.columns:
        df = addVelocities(drivedata)
        print("calling addVelocities()")

    v2 = df.LeadCarVelocity
    v1 = df.OwnshipVelocity
    cor = signal.correlate(v1 - v1.mean(), v2 - v2.mean(), mode="same")
    # cor-An N-dimensional array containing a subset of the discrete linear cross-correlation of in1 with in2.
    # delay index at the max
    df.insert(len(df.columns), "CrossCorrelations", cor, True)
    delayIndex = np.argmax(cor)
    if delayIndex > 0:
        v2 = df.LeadCarVelocity.iloc[delayIndex : df.columns.__len__()]
        v1 = df.OwnshipVelocity.iloc[delayIndex : df.columns.__len__()]
    # normalize vectors
    v1_norm = v1 / np.linalg.norm(v1)
    v2_norm = v2 / np.linalg.norm(v2)
    cor = np.dot(v1_norm, v2_norm)
    if cor > 0:
        return cor
    else:
        return 0.0


# find relative time where speed is within [mpsBound] of new speed limit
# 0 is when the car is crossing the sign.
# Returns None if the speed is never within 2
@registerMetric()
def speedLimitMatchTime(
    drivedata: pydre.core.DriveData, mpsBound: float, speedLimitCol: str
):
    required_col = ["DatTime", speedLimitCol, "Velocity"]
    diff = drivedata.checkColumns(required_col)

    speed_limit = drivedata.data.get_column(speedLimitCol).tail(1).item() * 0.44704
    starting_speed_limit = (
        drivedata.data.get_column(speedLimitCol).head(1).item() * 0.44704
    )

    if speed_limit == 0 or starting_speed_limit == 0:
        return None

    if speed_limit > starting_speed_limit:
        # increasing speed
        match_speed_block = drivedata.data.filter(
            pl.col("Velocity") >= (speed_limit - mpsBound)
        )
    else:
        match_speed_block = drivedata.data.filter(
            pl.col("Velocity") <= (speed_limit + mpsBound)
        )

    if match_speed_block.height > 0:
        time = match_speed_block.item(0, "DatTime")
    else:
        time = drivedata.data.tail(1).get_column("DatTime").item()

    sign_time = drivedata.data.filter(
        abs(pl.col(speedLimitCol) * 0.44704 - starting_speed_limit) > 0.1
    ).item(0, "DatTime")

    if time is None:
        return None
    else:
        # print( starting_speed_limit, speed_limit, time, sign_time)
        return time - sign_time


# The following functions need to be revised to work with polars rather than pandas

#
# @registerMetric(
#     columnnames=[
#         "total_time_onroad_glance",
#         "percent_onroad",
#         "avg_offroad",
#         "avg_onroad",
#     ]
# )
# def speedbumpHondaGaze(drivedata: pydre.core.DriveData):
#     required_col = ["DatTime", "gaze", "gazenum", "TaskNum", "taskblocks", "PartID"]
#     diff = drivedata.checkColumns(required_col)
#
#     numofglances = 0
#     df = pl.DataFrame(drivedata.data, columns=required_col)  # drop other columns
#     df = pl.DataFrame.drop_duplicates(
#         df.dropna(axis=0, how="any")
#     )  # remove nans and drop duplicates
#
#     if len(df) == 0:
#         return
#
#     # construct table with columns [glanceduration, glancelocation, error]
#     gr = df.groupby("gazenum", sort=False)
#     durations = gr["DatTime"].max() - gr["DatTime"].min()
#     locations = gr["gaze"].first()
#     error_list = gr["TaskNum"].any()
#
#     glancelist = pl.DataFrame(
#         {"duration": durations, "locations": locations, "errors": error_list}
#     )
#     glancelist["locations"].fillna("offroad", inplace=True)
#     glancelist["locations"].replace(
#         ["car.WindScreen", "car.dashPlane", "None"],
#         ["onroad", "offroad", "offroad"],
#         inplace=True,
#     )
#
#     glancelist_aug = glancelist
#     glancelist_aug["TaskNum"] = drivedata.data["TaskNum"].min()
#     glancelist_aug["taskblock"] = drivedata.data["taskblocks"].min()
#     glancelist_aug["Subject"] = drivedata.data["PartID"].min()
#
#     appendDFToCSV_void(glancelist_aug, "glance_list.csv")
#
#     # table constructed, now find metrics
#
#     num_onroad_glances = glancelist[(glancelist["locations"] == "onroad")][
#         "duration"
#     ].count()
#
#     total_time_onroad_glances = glancelist[(glancelist["locations"] == "onroad")][
#         "duration"
#     ].sum()
#     percent_onroad = total_time_onroad_glances / (
#         df["DatTime"].max() - df["DatTime"].min()
#     )
#
#     mean_time_offroad_glances = glancelist[(glancelist["locations"] == "offroad")][
#         "duration"
#     ].mean()
#     mean_time_onroad_glances = glancelist[(glancelist["locations"] == "onroad")][
#         "duration"
#     ].mean()
#
#     return [
#         total_time_onroad_glances,
#         percent_onroad,
#         mean_time_offroad_glances,
#         mean_time_onroad_glances,
#     ]
#
#
# @registerMetric(
#     columnnames=["85th_percentile", "duration_mean", "duration_median", "duration_std"]
# )
# def speedbumpHondaGaze2(
#     drivedata: pydre.core.DriveData, timecolumn="DatTime", maxtasknum=5
# ):
#     required_col = [
#         timecolumn,
#         "gaze",
#         "gazenum",
#         "TaskNum",
#         "TaskFail",
#         "TaskInstance",
#         "KEY_EVENT_T",
#         "KEY_EVENT_P",
#     ]
#     # filters.numberTaskInstances() is required.
#     # for now I just assume the input dataframe has a TaskInstance column
#     # diff = drivedata.checkColumns(required_col)
#
#     logger.warning("Processing Task {}".format(drivedata.data.TaskNum.mean()))
#     if drivedata.data.TaskNum.mean() == 0 or drivedata.data.TaskNum.mean() > maxtasknum:
#         return [None, None, None, None]
#     # if d.TaskNum.mean() == 4:
#     #    d.to_csv('4.csv')
#     df = pl.DataFrame(drivedata.data, columns=required_col)  # drop other columns
#     df = df.fillna(0)  # remove nans and drop duplicates
#
#     df["time_diff"] = df[
#         timecolumn
#     ].diff()  # get durations by calling time_column.diff()
#
#     df = df.loc[df.gaze != "onroad"]  # remove onroad rows
#     # df.to_csv('AAM_cp1.csv')
#     df = df.loc[
#         (df["TaskInstance"] != 0) & (df["TaskInstance"] != np.nan)
#     ]  # drop all rows that are not in any task instance
#     dropped_instances = df.loc[(df["TaskFail"] == 1)]
#     dropped_instances = (
#         dropped_instances["TaskInstance"].drop_duplicates()
#     )  # get all the task instances that contains a fail and needs to be dropped
#     df = df.loc[
#         ~df["TaskInstance"].isin(dropped_instances)
#     ]  # drop all the failed task instances
#     # df.to_csv('AAM_cp2.csv')
#
#     # get first 8 task instances
#     number_valid_instance = df["TaskInstance"].unique()
#     print(pl.unique(df.TaskInstance))
#     if len(number_valid_instance) > 8:
#         lowest_instance_no = number_valid_instance.min()
#         len_of_drop = len(
#             dropped_instances.loc[dropped_instances < (lowest_instance_no + 8)]
#         )
#         highest_instance_no = lowest_instance_no + 8 + len_of_drop
#         df = df.loc[
#             (df["TaskInstance"] < highest_instance_no)
#             & (df["TaskInstance"] >= lowest_instance_no)
#         ]
#         # logger.warning(highest_instance_no)
#         # logger.warning(lowest_instance_no)
#     elif len(number_valid_instance) < 8:
#         logger.warning(
#             "Not enough valid task instances. Found {}".format(
#                 len(number_valid_instance)
#             )
#         )
#
#     # df = df[df.TaskInstance < 9] # only keep the glance data for the first eight task instances for each task per person.
#
#     # print(df)
#     # df.to_csv('df.csv')
#
#     group_by_gazenum = df.groupby("gazenum", sort=False)
#     durations_by_gazenum = group_by_gazenum.sum()
#     durations_by_gazenum = durations_by_gazenum.loc[
#         (durations_by_gazenum["time_diff"] != 0.0)
#     ]
#     # print(durations_by_gazenum)
#     percentile = np.percentile(
#         durations_by_gazenum.time_diff, 85
#     )  # find the 85th percentile value (A1)
#
#     group_by_instance = df.groupby("TaskInstance", sort=False)  # A2
#     durations_by_instance = group_by_instance.sum()
#     print(durations_by_instance)
#     sum_mean = (durations_by_instance.time_diff).mean()  # mean of duration sum
#     sum_median = (durations_by_instance.time_diff).median()  # median of duration sum
#     sum_std = (durations_by_instance.time_diff).std()  # std of duration sum
#
#     return [percentile, sum_mean, sum_median, sum_std]


@registerMetric()
def eventCount(drivedata: pydre.core.DriveData, event="KEY_EVENT_S"):
    required_col = [event]
    diff = drivedata.checkColumns(required_col)

    df = pl.DataFrame(drivedata.data, columns=required_col)
    col_name = event + "_ocurrance"
    df[col_name] = df[event].diff()
    occur = df[col_name].value_counts().get(1)
    if occur == None:
        occur = 0
    return occur


@registerMetric()
def insDuration(drivedata: pydre.core.DriveData):
    required_col = ["DatTime", "TaskInstance"]
    diff = drivedata.checkColumns(required_col)

    df = pl.DataFrame(drivedata.data, columns=required_col)
    return df.tail(1).iat[0, 0] - df.head(1).iat[0, 0]


@registerMetric(
    columnnames=[
        "mean_onroad_spbpon",
        "mean_offroad_spbpon",
        "mean_onroad_spbpoff",
        "mean_offroad_spbpoff",
    ]
)
def speedbump2Gaze(drivedata: pydre.core.DriveData, timecolumn="DatTime", duration=6.0):
    required_col = [
        timecolumn,
        "gaze",
        "gazenum",
        "TaskNum",
        "TaskFail",
        "KEY_EVENT_S",
        "KEY_EVENT_T",
        "KEY_EVENT_P",
    ]
    diff = drivedata.checkColumns(required_col)

    if (
        drivedata.data.TaskNum.mean() == 0
        or drivedata.data.TaskNum.mean() < 4
        or drivedata.data.TaskNum.mean() > 5
    ):
        return [None, None, None, None]

    df = pl.DataFrame(drivedata.data, columns=required_col)  # drop other columns
    # df.to_csv("df.csv")
    # df = df.loc[(df['TaskInstance'] != 0) & (df['TaskInstance'] != np.nan)] # drop all rows that are not in any task instance
    # dropped_instances = df.loc[(df['TaskFail'] == 1)]
    # dropped_instances = dropped_instances['TaskInstance'].drop_duplicates() # get all the task instances that contains a fail and needs to be dropped
    # df = df.loc[~df['TaskInstance'].isin(dropped_instances)] # drop all the failed task instances

    event_s = pl.DataFrame(df, columns=[timecolumn, "gazenum", "gaze", "KEY_EVENT_S"])
    event_s["diff"] = event_s["KEY_EVENT_S"].diff()
    event_s["s_begin"] = 0
    event_s.loc[event_s["diff"] == 1, "s_begin"] = (
        1  # mark the beginning of all the s events
    )

    s_begin_time = event_s.loc[event_s["s_begin"] == 1]
    s_begin_time = s_begin_time.reset_index()
    # print(s_begin_time)
    index = 0
    for time in s_begin_time[timecolumn]:  # mark the duration of speedbump as 1
        event_s.loc[
            (event_s[timecolumn] > float(time))
            & (event_s[timecolumn] < float(time + duration)),
            "s_begin",
        ] = 1
        index += 1
    # event_s.to_csv("e.csv")

    group_by_gazenum = event_s.groupby("gazenum", sort=False)
    durations = pl.DataFrame(group_by_gazenum.sum(), columns=["s_begin"])

    durations_begin = pl.DataFrame(group_by_gazenum.min(), columns=[timecolumn])
    durations_begin = durations_begin.rename(columns={timecolumn: "begin"})
    durations_end = pl.DataFrame(group_by_gazenum.max(), columns=[timecolumn])
    durations_end = durations_end.rename(columns={timecolumn: "end"})

    durations["begin"] = durations_begin["begin"]
    durations["end"] = durations_end[
        "end"
    ]  # contains the beginning time and end time of all gazes
    durations = durations.reset_index()
    durations["gaze"] = group_by_gazenum.min()["gaze"].tolist()

    durations["in_speedbump"] = 0

    i = 0
    while i < len(durations):
        current_gaze = durations.at[i, "gazenum"]
        begin_time = durations.at[i, "begin"]
        end_time = durations.at[i, "end"]

        if durations.at[i, "s_begin"] > 0:
            temp = event_s.loc[event_s["gazenum"] == current_gaze]
            total_length = len(temp.index)  # length of the entire glance
            speedbump_act = temp.loc[
                temp["s_begin"] == 1
            ]  # length of the time period when speedbump is on during the current glance
            act_length = len(speedbump_act.index)
            if act_length >= (
                total_length / 2
            ):  # if speedbump is on for more than half of the total glance time:
                durations.at[i, "in_speedbump"] = 1
        i += 1

    durations["gaze_duration"] = durations["end"] - durations["begin"]

    durations_onroad_spbpon = durations.loc[
        (durations["gaze"] == "onroad") & (durations["in_speedbump"] == 1)
    ]
    durations_offroad_spbpon = durations.loc[
        (durations["gaze"] == "offroad") & (durations["in_speedbump"] == 1)
    ]
    durations_onroad_spbpoff = durations.loc[
        (durations["gaze"] == "onroad") & (durations["in_speedbump"] == 0)
    ]
    durations_offroad_spbpoff = durations.loc[
        (durations["gaze"] == "offroad") & (durations["in_speedbump"] == 0)
    ]

    # durations.to_csv("dursum.csv")
    # durations_onroad_spbpon.to_csv("duron_so.csv")
    # durations_offroad_spbpon.to_csv("duroff_so.csv")
    # durations_onroad_spbpoff.to_csv("duron_sx.csv")
    # durations_offroad_spbpoff.to_csv("duroff_sx.csv")

    mean_onroad_spbpon = durations_onroad_spbpon["gaze_duration"].mean()
    mean_offroad_spbpon = durations_offroad_spbpon["gaze_duration"].mean()
    mean_onroad_spbpoff = durations_onroad_spbpoff["gaze_duration"].mean()
    mean_offroad_spbpoff = durations_offroad_spbpoff["gaze_duration"].mean()
    return [
        mean_onroad_spbpon,
        mean_offroad_spbpon,
        mean_onroad_spbpoff,
        mean_offroad_spbpoff,
    ]
