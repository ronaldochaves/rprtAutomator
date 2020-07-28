# Standard imports
import os
import time as tm

# PyPI imports
import scipy.io as sio
from nptdms import TdmsFile

# Local imports
from tools import export_data

project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def var2channel(var_lst):
    """
    Using a Correspondence Matrix, it translates channel to engineering variable.
    """
    cor_matrix = {'time_HBM_LF': 'Channel_1_Data', 'CDP_IN': 'Channel_26_Data', 'CDP_OUT': 'Channel_33_Data',
                  'sync_HBM_LF': 'Channel_16_Data', 'FS_OUT': 'Channel_27_Data', 'FS_IN': 'Channel_28_Data',
                  'IMP_OUT': 'Channel_29_Data', 'VOL_Y': 'Channel_30_Data', 'BS_IN': 'Channel_31_Data',
                  'BS_OUT': 'Channel_32_Data', 'CDP_IN_RED': 'Channel_46_Data', 'VOL_X': 'Channel_51_Data',
                  'CDP_OUT_RED': 'Channel_52_Data', 'time_PXI1_LF': 'System Time', 'time_abs_PXI1_LF': 'Absolute Time',
                  'RP101SET': 'RP101SET', 'time_PXI2_LF': 'System Time', 'time_abs_PXI2_LF': 'Absolute Time',
                  'VE401': 'VE401', 'PT501': 'ai7'}
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


def extract_from_mat(file, var_lst):
    """
    Extract data from .mat accordingly to channels and export as a dict.
    """
    data = {}
    channels = var2channel(var_lst)
    for var, channel in zip(var_lst, channels):
        data[var] = sio.loadmat(file, squeeze_me=True)[channel]

    return data


def extract_from_tdms(file, var_lst):
    """
    Extract data from .tdms accordingly to channels and export as a dict.
    """
    data = {}
    channels = var2channel(var_lst)
    for var, channel in zip(var_lst, channels):
        data[var] = TdmsFile.read(file).groups()[0][channel][:]

    if is_waveform(TdmsFile.read(file).groups()[0][channels[0]]):
        data['time_PXI2_HF'] = TdmsFile.read(file).groups()[0][channels[0]].time_track()
        data['time_abs_PXI2_HF'] = TdmsFile.read(file).groups()[0][channels[0]].time_track(absolute_time=True,
                                                                                           accuracy='us')

    return data


def main(raw_files, var_lst_lst, data_dir_output):
    """
    Extract data from raw test files from a specific test_run and export it as a .csv file.
    """
    start_time = tm.time()
    print('Started data extraction.')
    print('...')
    for file, lst_var in zip(raw_files, var_lst_lst):
        file_name = os.path.splitext(os.path.basename(file))[0]
        outfile_path = os.path.join(data_dir_output, file_name + '_extracted.csv')
        if file.name.endswith('.tdms'):
            data = extract_from_tdms(file.path, lst_var)
            export_data.as_dict(data, outfile_path)
        elif file.name.endswith('.mat') or file.name.endswith('.MAT'):
            data = extract_from_mat(file.path, lst_var)
            export_data.as_dict(data, outfile_path)
    print('Finished data extraction from files [%.3f seconds]' % (tm.time() - start_time))
