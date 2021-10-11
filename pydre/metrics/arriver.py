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

        for idx in dt[alert_times].index:
            first_gaze_on_road_index = (dt.loc[idx:, "gaze"] == "onroad").idxmax()
            end_of_first_gaze_on_road_index = (dt.loc[first_gaze_on_road_index:, "gaze"] == "offroad").idxmax()
            glance_time = dt.loc[end_of_first_gaze_on_road_index].DatTime - dt.loc[first_gaze_on_road_index].DatTime
            glance_times.append(glance_time)

        if len(glance_times) == 0:
            return None
        else:
            return np.mean(np.asarray(glance_times))

def arrTimeTillLaneCenterAfterLaneLoss_crossingzero(drivedata: pydre.core.DriveData, center=0):
    """Find the time taken from a lane loss error and driver getting back to the center (after regain control)"""
    required_col = ["HTJAState", "HTJAReason", "Lane", "LaneOffset", "CEID"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:
        if dt.arrCriticalBlock.min() < 2 or dt.arrCriticalBlock.min() > 3:
            return "N/A"
        elif dt['SimDriverEngaged'].max() == 0:
            return "SimDriverEngage 0"
        elif dt['SimDriverEngaged'].min() == 1:
            return "SimDriverEngage 1"
        else: 
            try:
                print(dt.arrCriticalBlock.min())
                lane_loss_index = (dt.head(1)).index[0] # index when lane loss error occurs
                lost_control_index = dt.loc[dt['SimDriverEngaged'] == 1].head(1).index[0]
                lost_control = dt.loc[lost_control_index:]
                regain_control_index = (lost_control.loc[lost_control['SimDriverEngaged'] == 0].head(1)).index[0]
                after_regain_control = dt.loc[regain_control_index:]
                first_back_to_center = after_regain_control.loc[(after_regain_control['Lane'] == 2) & (after_regain_control['LaneOffset'] <= center)]
                back_to_center_index = first_back_to_center.head(1).index[0]

                print (dt.loc[back_to_center_index].DatTime)
                print (dt.loc[regain_control_index].DatTime)

                return dt.loc[back_to_center_index].DatTime - dt.loc[regain_control_index].DatTime
            except (IndexError):
                print ("IndexError: ", dt.SourceId.min())
                return None


def arrTimeTillLaneCenterAfterLaneLoss(drivedata: pydre.core.DriveData):
    """Find the time taken from a lane loss error and driver getting back to the center (after regain control)"""
    required_col = ["HTJAState", "HTJAReason", "Lane", "LaneOffset", "CEID"]
    dd = drivedata.checkColumns(required_col)

    for dt in drivedata.data:
        if dt['SimDriverEngaged'].max() == 0:
            return None #"SimDriverEngage 0"
        elif dt['SimDriverEngaged'].min() == 1:
            return None #"SimDriverEngage 1"
        else:
            try:
                lane_loss_index = (dt.head(1)).index[0] # index when lane loss error occurs
                lost_control_index = dt.loc[dt['SimDriverEngaged'] == 1].head(1).index[0]
                lost_control = dt.loc[lost_control_index:]
                regain_control_index = (lost_control.loc[lost_control['SimDriverEngaged'] == 0].head(1)).index[0]
                after_regain_control = dt.loc[regain_control_index:]
                center = (dt.loc[regain_control_index].LaneOffset) * 0.3
                if (dt.loc[regain_control_index].LaneOffset < 0.01):
                    return None #"at center when regain control"
                first_back_to_center = after_regain_control.loc[(after_regain_control['Lane'] == 2) & (after_regain_control['LaneOffset'] <= center)]
                back_to_center_index = first_back_to_center.head(1).index[0]

                return dt.loc[back_to_center_index].DatTime - dt.loc[regain_control_index].DatTime
            except (IndexError):
                return None


registerMetric('arrTimeToLookBackAfterInattentive', arrTimeToLookBackAfterInattentive)
registerMetric('arrTimeTillLaneCenterAfterLaneLoss', arrTimeTillLaneCenterAfterLaneLoss)
registerMetric('arrTimeTillLaneCenterAfterLaneLoss_crossingzero', arrTimeTillLaneCenterAfterLaneLoss_crossingzero)
registerMetric('arrTimeToDisengageAfterSlowAlert', arrTimeToDisengageAfterSlowAlert)
registerMetric('arrTimeToDisengageAfterStopAlert', arrTimeToDisengageAfterStopAlert)
registerMetric('arrTimeToDisengage', arrTimeToDisengage)
registerMetric("arrTimeAfterFailureToLookAtRoad", arrTimeAfterFailureToLookAtRoad)
registerMetric('arrMeanLengthOfFirstOnRoadGlanceAfterAlerts', arrMeanLengthOfFirstOnRoadGlanceAfterAlerts)
