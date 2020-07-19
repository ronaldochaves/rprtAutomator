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


# Convert epoch-based absolute time stamp (in seconds) from .tdms
def convert_from_ts(ts_lst):
    ts_lst = [float(ts) for ts in ts_lst]
    sys_epoch = tm.gmtime(0)
    ni_epoch = datetime(1904, 1, 1, tzinfo=timezone.utc)
    ref_epoch = datetime(sys_epoch.tm_year, sys_epoch.tm_mon, sys_epoch.tm_mday, tzinfo=timezone.utc)
    conv_dt = [ref_epoch + timedelta(seconds=ts_lst[i] + ni_epoch.timestamp()) for i in range(len(ts_lst))]

    return np.array(conv_dt)


# Convert epoch-based absolute numpy.datetime64 from .tdms
def convert_from_npdt64(npdt64_lst):
    npdt64_lst = [np.datetime64(npdt64) for npdt64 in npdt64_lst]
    sys_epoch = tm.gmtime(0)
    ref_epoch = np.datetime64(str(sys_epoch.tm_year) + '-' + str(sys_epoch.tm_mon).zfill(2) + '-' +
                              str(sys_epoch.tm_mday).zfill(2) + 'T00:00:00')
    conv_dt = []
    for i in range(len(npdt64_lst)):
        conv_dt.append(datetime.fromtimestamp((npdt64_lst[i] - ref_epoch)/np.timedelta64(1, 's'), timezone.utc))
    return np.array(conv_dt)


project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_input = os.path.join(project_dir, 'tests', 'test_outputs')
data_dir_output = os.path.join(project_dir, 'tests', 'test_outputs')
trim_factor = 0.05

# Pick test suite
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
        if ':' in key:
            data[key] = convert_from_npdt64(data[key])
        else:
            data[key] = convert_from_ts(data[key])
    else:
        data[key] = [float(value) for value in data[key]]

for key in data.keys():
    print(key)
    print(type(data[key]))
