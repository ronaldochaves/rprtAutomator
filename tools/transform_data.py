# Standard imports
import csv
import math
import os
import time as tm
from datetime import datetime, timezone, timedelta

# PyPI imports
import numpy as np
import scipy.io as sio
from nptdms import TdmsFile
from scipy.interpolate import interp1d


# Trim out size-specified borders from data
def trim(var_data, trim_ratio):
    border_size = math.floor(len(var_data) * trim_ratio)
    return var_data[border_size:-border_size]


# Convert [string of timestamp] to [datetime object]
def convert2dt(timestamp_lst):
    datetime_lst = []
    for ts in timestamp_lst:
        if ':' in ts:
            dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            dt_raw = datetime.fromtimestamp(float(ts), tz=timezone.utc)
            platform_epoch = datetime.fromtimestamp(tm.mktime(tm.localtime(0)), tz=timezone.utc)
            pxi_epoch = datetime(1904, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            dt = dt_raw - (platform_epoch - pxi_epoch)
            # print('dt_raw:', dt_raw, 'ts', dt_raw.timestamp())
            # print('platform_epoch:', platform_epoch, 'ts', platform_epoch.timestamp())
            # print('pxi_epoch:', pxi_epoch, 'ts', pxi_epoch.timestamp())
            # print('dt:', dt, 'ts', dt.timestamp())
        datetime_lst.append(dt)
    return np.array(datetime_lst)


project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_input = os.path.join(project_dir, 'tests', 'test_outputs')
data_dir_output = os.path.join(project_dir, 'tests', 'test_outputs')
trim_factor = 0.05

# Pick extracted .csv files
csv_files = []
for entry in sorted(os.scandir(data_dir_input), key=lambda ent: ent.name):
    if entry.is_file() and entry.name.endswith('_extracted.csv') and not entry.name.startswith('.'):
        csv_files.append(entry.path)

# Load data
data = {}
for file in csv_files:
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for key in reader.fieldnames:
            data[key] = []
        for row in reader:
            for key in reader.fieldnames:
                data[key].append(row[key])

# Trim spurious values
for key in data.keys():
    data[key] = trim(data[key], trim_factor)

# Convert values
for key in data.keys():
    if key.startswith('time_abs_'):
        print('key:', key, '- value:', data[key][0], '- type:', type(data[key][0]))
        data[key] = convert2dt(data[key])
        print('key:', key, '- value:', data[key][0], '- type:', type(data[key][0]))
    else:
        data[key] = [float(value) for value in data[key]]

# for key in data.keys():
#     print('key:', key, 'type:', type(data[key]))
