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


# # Convert [string of timestamp] to [datetime object]
# def convert2dt(timestamp_lst):
#     """
#     Convert a list of timestamp (as strings) to a list of datetime.datetime object
#     """
#     datetime_lst = []
#     for ts in timestamp_lst:
#         if ':' in ts:
#             dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
#         else:
#             dt_raw = datetime.fromtimestamp(float(ts), tz=timezone.utc)
#             platform_epoch = datetime.fromtimestamp(tm.mktime(tm.localtime(0)), tz=timezone.utc)
#             pxi_epoch = datetime(1904, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
#             dt = dt_raw - (platform_epoch - pxi_epoch)
#             # print('dt_raw:', dt_raw, 'ts', dt_raw.timestamp())
#             # print('platform_epoch:', platform_epoch, 'ts', platform_epoch.timestamp())
#             # print('pxi_epoch:', pxi_epoch, 'ts', pxi_epoch.timestamp())
#             # print('dt:', dt, 'ts', dt.timestamp())
#         datetime_lst.append(dt)
#     return np.array(datetime_lst)


def convert_data_type(data):
    """
    Convert data type to datetime.datetime object or float.
    """
    for key in data.keys():
        if key.startswith('time_abs_'):
            timestamp_lst = []
            for ts in data[key]:
                if ':' in ts:
                    dt = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
                else:
                    dt_raw = datetime.fromtimestamp(float(ts), tz=timezone.utc)
                    platform_epoch = datetime.fromtimestamp(tm.mktime(tm.localtime(0)), tz=timezone.utc)
                    pxi_epoch = datetime(1904, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
                    dt = dt_raw - (platform_epoch - pxi_epoch)
                timestamp_lst.append(dt)
            data[key] = np.array(timestamp_lst)
        else:
            data[key] = np.array(list(map(float, data[key])))
    return data


def abs2rel(time_abs, time_abs_ref=None):
    """
    Create a relative time from an absolute time and a reference.
    """
    time_rel = np.array([])
    if time_abs_ref is None:
        time_abs_ref = time_abs[0]
    for t_abs in time_abs:
        time_rel = np.append(time_rel, (t_abs - time_abs_ref).total_seconds())
    return time_rel


def create_time_abs(time_rel, time_abs_event, time_offset):
    """
    Create an absolute time based on the delay of a given 'event' and its relative time.
    """
    time_abs_offset = time_abs_event - timedelta(seconds=time_offset)
    time_abs = [time_abs_offset]
    deltas = np.diff(time_rel)
    for delta in deltas:
        time_abs.append(time_abs[-1] + timedelta(seconds=delta))

    return np.array(time_abs)


def set_interp_interval(time_abs_lst):
    # Set maximum common interval between absolute times
    left_common = max([time_abs[0] for time_abs in time_abs_lst])
    right_common = min([time_abs[-1] for time_abs in time_abs_lst])

    # Set interpolation interval
    minimum_delta = np.inf
    for time_abs in time_abs_lst:
        delta = (time_abs[1] - time_abs[0]).total_seconds()
        minimum_delta = min(minimum_delta, delta)
    interp_length = (right_common - left_common).total_seconds()
    interp_num_elem = math.floor(interp_length/minimum_delta) - 1
    interp_abs_start = left_common + timedelta(seconds=minimum_delta)
    interp_abs = [interp_abs_start + timedelta(seconds=i*minimum_delta) for i in range(interp_num_elem)]
    interp_rel = abs2rel(interp_abs)
    return interp_abs, interp_rel


def main(extracted_files, data_dir_output):
    # Extract data
    start_time = tm.time()
    print('Started data transformation.')
    print('...')

    # Load data
    data_lst = []
    for file in extracted_files:
        data = {}
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            var_lst = reader.fieldnames
            for key in var_lst:
                data[key] = []
            for row in reader:
                for key in var_lst:
                    data[key].append(row[key])

        # Trim spurious values
        trim_factor = 0.05
        for key in data.keys():
            data[key] = trim(data[key], trim_factor)

        # Change variable dtypes
        data_lst.append(convert_data_type(data))

    for data in data_lst:
        if not 'time_abs' in data.keys():
            # Create absolute time for HBM DAQ based on the delay of a given 'event'
            pass
            key_time_rel = [key for key in data.keys() if key.startswith('time_')][0]
            time_rel = data[key_time_rel]
            time_abs_event = datetime.strptime('2020-07-14T12:30:30.179560', '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
            time_offset = 0
            data[key_time_rel.replace('time_', 'time_abs_')] = create_time_abs(time_rel, time_abs_event, time_offset)

        # Redefine relative times
        for key in data.keys():
            if key.startswith('time_abs_'):
                data[key.replace('abs_', '')] = abs2rel(data[key], data[key][0])

    # Set interpolation interval
    time_abs_lst = []
    for data in data_lst:
        for key in data.keys():
            if key.startswith('time_abs_'):
                time_abs_lst.append(data[key])
    interp_abs, interp_rel = set_interp_interval(time_abs_lst)

    # Interpolate all data
    data_interpolated = {'time_abs': interp_abs, 'time': interp_rel}
    for data in data_lst:
        data_time = [data[key] for key in data.keys() if key.startswith('time_') and not key.startswith('time_abs_')][0]
        for key in data.keys():
            if not key.startswith('time_'):
                interp_function = interp1d(data_time, data[key])
                data_interpolated[key] = interp_function(interp_rel)

    # Export transformed data
    outfile_path = os.path.join(data_dir_output, 'example_transformed.csv')
    export_data.as_dict(data_interpolated, outfile_path)

    print('Finished data transformation [%.3f seconds]' % (tm.time() - start_time))
