from __future__ import annotations # needed for python < 3.9

import numpy as np

import pydre.core
from pydre.metrics import registerMetric


def arrTimeToLookBackAfterInattentive(drivedata: pydre.core.DriveData):
    """Find the length of time between the first inattentive alert and the first glance on the road"""
    required_col = ["HTJAState", "HTJAReason"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:
        try:
            first_inattentive = dt[(dt.HTJAState == 11) & (dt.HTJAReason == 1)].head(1)
            first_inattentive_index = first_inattentive.index[0]
            first_gaze_on_road = (dt.loc[first_inattentive_index:, "gaze"] == "onroad").idxmax()
            return dt.loc[first_gaze_on_road].DatTime - dt.loc[first_inattentive_index].DatTime
        except (KeyError, IndexError):
            # block is not valid
            return None


def arrTimeToDisengageAfterSlowAlert(drivedata: pydre.core.DriveData):
    """Find the length of time between the first slowing alert and the first glance on the road"""
    required_col = ["HTJAState", "HTJAReason"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:
        try:
            first_inattentive = dt[(dt.HTJAState == 6) & (dt.HTJAReason == 1)].head(1)
            first_inattentive_index = first_inattentive.index[0]
            first_disengaged = (dt.loc[first_inattentive_index:, "SimDriverEngaged"] == 0).idxmax()
            return dt.loc[first_disengaged].DatTime - dt.loc[first_inattentive_index].DatTime
        except (KeyError, IndexError):
            # block is not valid
            return None

def arrTimeToDisengageAfterStopAlert(drivedata: pydre.core.DriveData):
    """Find the length of time between the first stopping alert and the first glance on the road"""
    required_col = ["HTJAState", "HTJAReason"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:
        try:
            first_inattentive = dt[(dt.HTJAState == 7) & (dt.HTJAReason == 1)].head(1)
            first_inattentive_index = first_inattentive.index[0]
            first_disengaged = (dt.loc[first_inattentive_index:, "SimDriverEngaged"] == 0).idxmax()
            return dt.loc[first_disengaged].DatTime - dt.loc[first_inattentive_index].DatTime
        except (KeyError, IndexError):
            # block is not valid
            return None



def arrTimeToDisengage(drivedata: pydre.core.DriveData):
    """Find the length of time between the first inattentive alert and the first glance on the road"""
    required_col = ["HTJAState", "HTJAReason"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:
        try:
            first_disengaged = (dt.loc[:, "SimDriverEngaged"] == 0).idxmax()
            return dt.loc[first_disengaged].DatTime - dt.DatTime.iloc[0]
        except (KeyError, IndexError):
            # block is not valid
            return None


def arrTimeAfterFailureToLookAtRoad(drivedata: pydre.core.DriveData):
    """Find the length of time between the first inattentive alert and the first glance on the road"""
    required_col = ["HTJAState", "HTJAReason"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:
        try:
            first_failure = dt[(dt.CEID != 0)].head(1)
            first_failure_index = first_failure.index[0]
            first_gaze_on_road_index = (dt.loc[first_failure_index:, "gaze"] == "onroad").idxmax()
            return dt.loc[first_gaze_on_road_index].DatTime - dt.loc[first_failure_index].DatTime
        except (KeyError, IndexError):
            # block is not valid
            return None


def arrMeanLengthOfFirstOnRoadGlanceAfterAlerts(drivedata: pydre.core.DriveData):
    """Average Time of On-Road Attention"""
    required_col = ["HTJAState", "HTJAReason"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:

        # find all inattentive alerts:
        alert_diff = dt["HTJAState"].diff()

        alert_times = (alert_diff != 0) & (dt["HTJAState"] == 11)
        if dt.iloc[0].HTJAState == 11:
            alert_times.iloc[0] = True

        glance_times = []

        for idx in dt[alert_times].index():
            first_gaze_on_road_index = (dt.loc[first_failure_index:, "gaze"] == "onroad").idxmax()
            end_of_first_gaze_on_road_index = (dt.loc[first_gaze_on_road_index:, "gaze"] == "offroad").idxmax()
            glance_time = dt.loc[end_of_first_gaze_on_road_index].DatTime - dt.loc[first_gaze_on_road_index].DatTime
            glance_times.append(glance_times)

        return np.mean(np.asarray(glance_times))


registerMetric('arrTimeToLookBackAfterInattentive', arrTimeToLookBackAfterInattentive)
registerMetric('arrTimeToDisengageAfterRedAlert', arrTimeToDisengageAfterSlowAlert)
registerMetric('arrTimeToDisengageAfterStopAlert', arrTimeToDisengageAfterStopAlert)
registerMetric('arrTimeToDisengage', arrTimeToDisengage)
registerMetric("arrTimeAfterFailureToLookAtRoad", arrTimeAfterFailureToLookAtRoad)

