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



registerMetric('arrTimeToLookBackAfterInattentive', arrTimeToLookBackAfterInattentive)
registerMetric('arrTimeToDisengageAfterRedAlert', arrTimeToDisengageAfterRedAlert)