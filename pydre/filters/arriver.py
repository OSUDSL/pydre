import numpy as np
import pandas

import pydre.core


def arrDefineCriticalBlocks(drivedata: pydre.core.DriveData):
    # define a new column in the data object that
    for idx, data, in enumerate(drivedata.data):
        dt = pandas.DataFrame(data)

        dt["Critical Point"] = ""
        # find blocks when the car is stopped
        stopping_delta = 0.1 # a stop is when the car is moving under 0.1 m/s
        dt["isStopped"] = dt["Velocity"] < stopping_delta
        dt['stoppingBlock'] = (dt['isStopped'].shift(1) != dt['isStopped']).astype(int).cumsum()
        dt['stoppingBlock'] = dt['stoppingBlock'] * dt['isStopped']
        # find only blocks when the car is stopped for more than 10 seconds

        gr = dt.groupby('stoppingBlock', sort=False)
        agg = gr.DatTime.agg([np.min, np.max])
        long_enough = (agg['amax'] - agg['amin']) > 10  # block larger than 10s
        long_enough = long_enough[1:][long_enough].index.to_list() # list of the block ids that are long enough to count as stops
        all_stops = gr.groups.keys()
        too_short = set(all_stops) - set(long_enough)
        dt.loc[dt.stoppingBlock.isin(too_short), "stoppingBlock"] = 0
        stopping_times = agg.loc[long_enough]

        dt['CEIDChanged'] = (dt['CEID'].shift(-1) != dt['CEID'])


        # find first inattentive
        try:
            first_inattentive = dt[(dt.HTJAState == 11) & (dt.HTJAReason == 1)].head(1)
            first_inattentive_index = first_inattentive.index[0]
            first_stop = (dt.loc[first_inattentive_index:, "stoppingBlock"] > 0).idxmax()
            dt.loc[first_inattentive_index:first_stop, "arrCriticalBlock"] = "HTJA"
        except (KeyError, IndexError):
            # block is not valid
            pass

        # find alerted lane loss
        try:
            last_event_start = dt[(dt.CEIDChanged == 1) & (dt.CEID == 1) & (dt.HTJAReason == 4)].head(1)
            last_event_start_index = last_event_start.index[0]
            first_stop = (dt.loc[last_event_start_index:, "stoppingBlock"] > 0).idxmax()
            dt.loc[last_event_start_index:first_stop, "arrCriticalBlock"] = "AlertF Lane"
        except (KeyError, IndexError):
            #  block is not valid
            pass

        # find silent lane loss
        try:
            last_event_start = dt[(dt.CEIDChanged == 1) & (dt.CEID == 1) & (dt.HTJAReason == 0)].head(1)
            last_event_start_index = last_event_start.index[0]
            first_stop = (dt.loc[last_event_start_index:, "stoppingBlock"] > 0).idxmax()
            dt.loc[last_event_start_index:first_stop, "arrCriticalBlock"] = "SilentF Lane"
        except (KeyError, IndexError):
            #  block is not valid
            pass

        # find alerted lead car loss
        try:
            last_event_start = dt[(dt.CEIDChanged == 1) & (dt.CEID == 2)].head(1)
            last_event_start_index = last_event_start.index[0]
            first_stop = (dt.loc[last_event_start_index:, "stoppingBlock"] > 0).idxmax()
            dt.loc[last_event_start_index:first_stop, "arrCriticalBlock"] = "AlertF LeadLoss"
        except (KeyError, IndexError):
            #  block is not valid
            pass

        # find silent lead car loss
        try:
            last_event_start = dt[(dt.CEIDChanged == 1) & (dt.CEID == 5)].head(1)
            last_event_start_index = last_event_start.index[0]
            first_stop = (dt.loc[last_event_start_index:, "stoppingBlock"] > 0).idxmax()
            dt.loc[last_event_start_index:first_stop, "arrCriticalBlock"] = "SilentF LeadLoss"
        except (KeyError, IndexError):
            #  block is not valid
            pass

        # find keylockout speed alert
        try:
            first_event = dt[(dt.HTJAState == 31)].head(1)
            first_event_index = first_event.index[0]
            first_stop = (dt.loc[first_event_index:, "stoppingBlock"] > 0).idxmax()
            dt.loc[first_event_index:first_stop, "arrCriticalBlock"] = "Lockout"
        except (KeyError, IndexError):
            #  block is not valid
            pass


        # find high to low speed alert
        try:
            first_event = dt[(dt.HTJAReason == 31)].head(1)
            first_event_index = first_event.index[0]
            first_stop = (dt.loc[first_event_index:, "stoppingBlock"] > 0).idxmax()
            dt.loc[first_event_index:first_stop, "arrCriticalBlock"] = "TA"
        except (KeyError, IndexError):
            #  block is not valid
            pass

        drivedata.data[idx] = dt
    return drivedata