import numpy as np
import pandas as pd

def evt_to_df(filename):
    with open(filename, 'r') as f:
        line = f.readline()
        col_names = line.strip().split(' ')
        col_names.insert(3, 'temp')
        line = f.readline()
        events = []
        while line:
            events.append(line.strip().split(' '))
            line = f.readline()
    events = np.array(events).T
    return pd.DataFrame({col: row for col, row in zip(col_names, events)})

if __name__ == '__main__':
    event_file = input('Event file: ')
    event_df = evt_to_df(event_file)
    print(event_df.head())
