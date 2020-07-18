# Standard imports
import csv
import os
import time as tm

# PyPI imports
import numpy
import scipy.io as sio
from nptdms import TdmsFile


proj_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def var2channel(vars):
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
    for var in vars:
        channels.append(cor_matrix[var])

    return channels


def is_waveform(channel):
    try:
        channel.time_track()
        return True
    except KeyError:  # KeyError if channel doesn't have waveform data (info from npTDMS package)
       return False

def extract_from_mat(file, vars, output_dir):
    """
    Extract data from .mat accordingly to channels and export as a .csv file.
    """
    data = {}
    channels = var2channel(vars)
    for var, channel in zip(vars, channels):
        data[var] = sio.loadmat(file, squeeze_me=True)[channel]

    file_name = os.path.splitext(os.path.basename(file))[0]
    output_dir = os.path.join(proj_dir, 'tests', 'test_outputs')
    outfile_path = os.path.join(output_dir, file_name + '_extracted.csv')
    with open(outfile_path, 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(vars)
        writer.writerows(zip(*[data[var] for var in vars]))


def extract_from_tdms(file, vars, output_dir):
    """
    Extract data from .tdms accordingly to channels and export as a .csv file.
    """
    data = {}
    channels = var2channel(vars)
    for var, channel in zip(vars, channels):
        data[var] = TdmsFile.read(file).groups()[0][channel][:]

    if is_waveform(TdmsFile.read(file).groups()[0][channels[0]]):
        data['time_PXI2_HF'] = TdmsFile.read(file).groups()[0][channels[0]].time_track()
        data['time_abs_PXI2_HF'] = TdmsFile.read(file).groups()[0][channels[0]].time_track(absolute_time=True)
        vars = ['time_PXI2_HF', 'time_abs_PXI2_HF'] + vars

    file_name = os.path.splitext(os.path.basename(file))[0]
    outfile_path = os.path.join(output_dir, file_name + '_extracted.csv')
    with open(outfile_path, 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(vars)
        writer.writerows(zip(*[data[var] for var in vars]))


def main(raw_files, lst_vars, output_dir):

    # Extract data
    start_time = tm.time()
    print('Started data extraction.')
    print('...')
    for file, vars in zip(raw_files, lst_vars):
        if file.name.endswith('.tdms'):
            extract_from_tdms(file.path, vars, output_dir)
        if file.name.endswith('.mat'):
            extract_from_mat(file.path, vars, output_dir)
    print('Finished data extraction from files: %.3f seconds' % (tm.time() - start_time))

if __name__ == '__main__':
    input_dir = os.path.join(proj_dir, 'tests', 'test_inputs')
    output_dir = os.path.join(proj_dir, 'tests', 'test_outputs')

    file1 = os.path.join(input_dir, 'example_matfile.mat')
    vars1 = ['time_HBM_LF', 'CDP_IN', 'CDP_OUT']
    extract_from_mat(file1, vars1, output_dir)

    file2 = os.path.join(input_dir, 'example_01.tdms')
    vars2 = ['time_PXI1_LF', 'time_abs_PXI1_LF', 'RP101SET']
    extract_from_tdms(file2, vars2, output_dir)

    file3 = os.path.join(input_dir, 'example_02.tdms')
    vars3 = ['time_PXI2_LF', 'time_abs_PXI2_LF', 'VE401']
    extract_from_tdms(file3, vars3, output_dir)

    file4 = os.path.join(input_dir, 'example_03.tdms')
    vars4 = ['PT501']
    extract_from_tdms(file4, vars4, output_dir)
