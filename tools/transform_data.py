# Standard imports
import csv
import math
import os
import time as tm
from datetime import datetime, timezone, timedelta

# PyPI imports
import numpy as np
from scipy.interpolate import interp1d

# Local imports
from tools import export_data

project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Trim out size-specified borders from data
def trim(var_data, trim_ratio):
    border_size = math.floor(len(var_data) * trim_ratio)
    return var_data[border_size:-border_size]


# Convert [string of timestamp] to [datetime object]
def convert2dt(timestamp_lst):
    datetime_lst = []
    for ts in timestamp_lst:
        if ':' in ts:
            dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
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


def change_dtype(data):
    # Change variable dtypes
    print('Started variable dtypes change')

    start_time = tm.time()
    for key in data.keys():
        if key.startswith('time_abs_'):
            data[key] = convert2dt(data[key])
        else:
            data[key] = np.array(list(map(float, data[key])))

    print('Finished variable dtypes change [%.3f seconds]' % (tm.time() - start_time))
    return data


def abs2rel(time_abs, time_abs_ref=None):
    time_rel = np.array([])
    if time_abs_ref is None:
        time_abs_ref = time_abs[0]
    for t_abs in time_abs:
        time_rel = np.append(time_rel, (t_abs - time_abs_ref).total_seconds())
    return time_rel


def main(extracted_files, data_dir_output):

    # Extract data
    start_time = tm.time()
    print('Started data transformation.')
    print('...')

    # Load data
    data = {}
    for file in extracted_files:
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            for key in reader.fieldnames:
                data[key] = []
            for row in reader:
                for key in reader.fieldnames:
                    data[key].append(row[key])

    # Trim spurious values
    trim_factor = 0.05
    for key in data.keys():
        data[key] = trim(data[key], trim_factor)

    # Change variable dtypes
    data = change_dtype(data)

    # Create absolute time for HBM DAQ based on the delay of a given 'event'
    pass
    time_abs_event = data['time_abs_PXI1_LF'][0]
    time_abs_offset = time_abs_event - timedelta(seconds=data['time_HBM_LF'][0])
    data['time_abs_HBM_LF'] = [time_abs_offset]
    deltas = np.diff(data['time_HBM_LF'])
    for delta in deltas:
        data['time_abs_HBM_LF'].append(data['time_abs_HBM_LF'][-1] + timedelta(seconds=delta))

    # Redefine relative times
    for key in data.keys():
        if key.startswith('time_abs_'):
            # print('key:', key, 'value:', data[key][0])
            data[key.replace('abs_', '')] = abs2rel(data[key], data[key][0])

    # Set maximum common interval between absolute times
    left_common = max([data[key][0] for key in data.keys() if key.startswith('time_abs_')])
    right_common = min([data[key][-1] for key in data.keys() if key.startswith('time_abs_')])

    # Set interpolation interval
    minimum_delta = np.inf
    for key in data.keys():
        if key.startswith('time_abs_'):
            deltas = np.diff(data[key.replace('abs_', '')])
            minimum_delta = min(minimum_delta, np.mean(deltas))
    interp_length = (right_common - left_common).total_seconds()
    interp_len = math.floor(interp_length/minimum_delta) - 1
    interp_abs_start = left_common + timedelta(seconds=minimum_delta)
    interp_abs = [interp_abs_start + timedelta(seconds=i*minimum_delta) for i in range(interp_len)]
    interp_rel = abs2rel(interp_abs)

    # Interpolate all data
    data_interpolated = {'time_abs': interp_abs, 'time': interp_rel}

    for key in data.keys():
        if key in ['CDP_IN', 'CDP_OUT']:
            interp_time = abs2rel(interp_abs, data['time_abs_HBM_LF'][0])
            interp_function = interp1d(data['time_HBM_LF'], data[key])
            data_interpolated[key] = interp_function(interp_time)
        elif key in ['RP101SET']:
            interp_time = abs2rel(interp_abs, data['time_abs_PXI1_LF'][0])
            interp_function = interp1d(data['time_PXI1_LF'], data[key])
            data_interpolated[key] = interp_function(interp_time)
        elif key in ['VE401']:
            interp_time = abs2rel(interp_abs, data['time_abs_PXI2_LF'][0])
            interp_function = interp1d(data['time_PXI2_LF'], data[key])
            data_interpolated[key] = interp_function(interp_time)
        elif key in ['PT501']:
            interp_time = abs2rel(interp_abs, data['time_abs_PXI2_HF'][0])
            interp_function = interp1d(data['time_PXI2_HF'], data[key])
            data_interpolated[key] = interp_function(interp_time)

    # Export transformed data
    outfile_path = os.path.join(data_dir_output, 'example_transformed.csv')
    export_data.as_dict(data_interpolated, outfile_path)

    print('Finished data transformation [%.3f seconds]' % (tm.time() - start_time))
