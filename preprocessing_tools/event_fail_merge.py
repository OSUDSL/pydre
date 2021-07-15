import argparse
import os
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_directory', help='Input directory')
parser.add_argument('-o', '--output_directory', help='Output directory')
parser.add_argument('-e', '--event_file', help='Event file')
parser.add_argument('-t', '--timestamp_file', help='Timestamp file')
args = parser.parse_args()

# C:\Users\Craig\Documents\Work\DSL\input
# C:\Users\Craig\Documents\Work\DSL\output

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

if args.input_directory and args.output_directory and args.event_file and args.timestamp_file:
    event_df = evt_to_df(os.path.join(args.input_directory, args.event_file))
    timestamp_df = pd.read_excel(os.path.join(args.input_directory, args.timestamp_file))['SimTime'].iloc[:-1]
    for timestamp in timestamp_df:
        timestamp = '%.2f'%float(timestamp)
        for index, event in enumerate(event_df.iterrows()):
            if float(timestamp) < float(event[1][1]):
                event_df.iloc[index] = [timestamp, timestamp, timestamp, timestamp, 'KEY_EVENT_F']
                break
    with open(os.path.join(args.output_directory, args.event_file), 'w') as f:
        for event in event_df.iterrows():
            f.write(' '.join([str(item) for item in event[1]]) + '\n')
else:
    print('Usage: py event_fail_merge.py -i <input-directory> -o <output-directory> -e <event-file> -t <timestamp-file>')

