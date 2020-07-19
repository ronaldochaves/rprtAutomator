# Standard imports
import csv
import os
import time as tm

# PyPI imports
import numpy as np
import scipy.io as sio
from nptdms import TdmsFile


project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def var2channel(var_lst):
    """
    Using a Correspondence Matrix, it translates channel to engineering variable.
    """
    cor_matrix = {'time_HBM_LF':'Channel_1_Data', 'CDP_IN':'Channel_26_Data', 'CDP_OUT':'Channel_33_Data',
                  'sync_HBM_LF':'Channel_16_Data', 'FS_OUT':'Channel_27_Data', 'FS_IN':'Channel_28_Data',
                  'IMP_OUT':'Channel_29_Data', 'VOL_Y':'Channel_30_Data', 'BS_IN':'Channel_31_Data',
                  'BS_OUT': 'Channel_32_Data', 'CDP_IN_RED':'Channel_46_Data', 'VOL_X': 'Channel_51_Data',
                  'CDP_OUT_RED':'Channel_52_Data', 'time_PXI1_LF':'System Time', 'time_abs_PXI1_LF':'Absolute Time',
                  'RP101SET':'RP101SET', 'time_PXI2_LF':'System Time', 'time_abs_PXI2_LF':'Absolute Time',
                  'VE401':'VE401', 'PT501':'ai7'}
    channels = []
    for var in var_lst:
        channels.append(cor_matrix[var])

    return channels


def is_waveform(channel):
    try:
        channel.time_track()
        return True
    except KeyError:  # KeyError if channel doesn't have waveform data (info from npTDMS package)
        return False


def data_as_dict_rows(data, num_rows):
    data_rows = []
    for i in range(num_rows):
        row = {}
        for key in data.keys():
            row[key] = data[key][i]
        data_rows.append(row)
    return data_rows


def extract_from_mat(file, var_lst, data_dir_output):
    """
    Extract data from .mat accordingly to channels and export as a .csv file.
    """
    data = {}
    channels = var2channel(var_lst)
    for var, channel in zip(var_lst, channels):
        data[var] = sio.loadmat(file, squeeze_me=True)[channel]

    data_rows = data_as_dict_rows(data, len(data[var_lst[0]]))

    file_name = os.path.splitext(os.path.basename(file))[0]
    outfile_path = os.path.join(data_dir_output, file_name + '_extracted.csv')
    with open(outfile_path, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=var_lst, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)


def extract_from_tdms(file, var_lst, data_dir_output):
    """
    Extract data from .tdms accordingly to channels and export as a .csv file.
    """
    data = {}
    channels = var2channel(var_lst)
    for var, channel in zip(var_lst, channels):
        data[var] = TdmsFile.read(file).groups()[0][channel][:]

    if is_waveform(TdmsFile.read(file).groups()[0][channels[0]]):
        data['time_PXI2_HF'] = TdmsFile.read(file).groups()[0][channels[0]].time_track()
        data['time_abs_PXI2_HF'] = TdmsFile.read(file).groups()[0][channels[0]].time_track(absolute_time=True)
        data['time_abs_PXI2_HF'] = [(ts - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's') for ts in data['time_abs_PXI2_HF']]
        var_lst = ['time_PXI2_HF', 'time_abs_PXI2_HF'] + var_lst

    data_rows = data_as_dict_rows(data, len(data[var_lst[0]]))

    file_name = os.path.splitext(os.path.basename(file))[0]
    outfile_path = os.path.join(data_dir_output, file_name + '_extracted.csv')
    with open(outfile_path, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=var_lst, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)


def main(raw_files, var_lst_lst, data_dir_output):

    # Extract data
    start_time = tm.time()
    print('Started data extraction.')
    print('...')
    for file, lst_var in zip(raw_files, var_lst_lst):
        if file.name.endswith('.tdms'):
            extract_from_tdms(file.path, lst_var, data_dir_output)
        if file.name.endswith('.mat'):
            extract_from_mat(file.path, lst_var, data_dir_output)
    print('Finished data extraction from files: %.3f seconds' % (tm.time() - start_time))
