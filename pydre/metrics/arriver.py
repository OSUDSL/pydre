from __future__ import annotations # needed for python < 3.9

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


def arrTimeToDisengageAfterRedAlert(drivedata: pydre.core.DriveData):
    """Find the length of time between the first inattentive alert and the first glance on the road"""
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


def arrTimeTillLaneCenterAfterLaneLoss(drivedata: pydre.core.DriveData, center=0):
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


def arrTimeTillLaneCenterAfterLaneLoss_1(drivedata: pydre.core.DriveData):
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
            
            #dt.to_csv('temp.csv')
            lane_loss_index = (dt.head(1)).index[0] # index when lane loss error occurs
            lost_control_index = dt.loc[dt['SimDriverEngaged'] == 1].head(1).index[0]
            lost_control = dt.loc[lost_control_index:]
            regain_control_index = (lost_control.loc[lost_control['SimDriverEngaged'] == 0].head(1)).index[0]
            after_regain_control = dt.loc[regain_control_index:]
            center = (dt.loc[regain_control_index].LaneOffset) * 0.3
            if (dt.loc[regain_control_index].LaneOffset < 0.01):
                return "at center when regain control"
            print(center)
            #after_regain_control.to_csv('temp_regain.csv')
            first_back_to_center = after_regain_control.loc[(after_regain_control['Lane'] == 2) & (after_regain_control['LaneOffset'] <= center)]
            back_to_center_index = first_back_to_center.head(1).index[0]

            print (dt.loc[back_to_center_index].DatTime)
            print (dt.loc[regain_control_index].DatTime)

            return dt.loc[back_to_center_index].DatTime - dt.loc[regain_control_index].DatTime
            


registerMetric('arrTimeToLookBackAfterInattentive', arrTimeToLookBackAfterInattentive)
registerMetric('arrTimeToDisengageAfterRedAlert', arrTimeToDisengageAfterRedAlert)
registerMetric('arrTimeTillLaneCenterAfterLaneLoss', arrTimeTillLaneCenterAfterLaneLoss)