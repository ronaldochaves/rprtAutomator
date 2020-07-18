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


# Convert epoch-based absolute time stamp (in seconds) from .tdms
def convert_from_ts(ts):
    sys_epoch = tm.gmtime(0)
    ni_epoch = datetime(1904, 1, 1, tzinfo=timezone.utc)
    ref_epoch = datetime(sys_epoch.tm_year, sys_epoch.tm_mon, sys_epoch.tm_mday, tzinfo=timezone.utc)
    conv_dt = [ref_epoch + timedelta(seconds=ts[i] + ni_epoch.timestamp()) for i in range(len(ts))]

    return conv_dt


# Convert epoch-based absolute numpy.datetime64 from .tdms
def convert_from_npdt64(npdt64):
    sys_epoch = tm.gmtime(0)
    ref_epoch = np.datetime64(str(sys_epoch.tm_year) + '-' + str(sys_epoch.tm_mon).zfill(2) + '-' +
                              str(sys_epoch.tm_mday).zfill(2) + 'T00:00:00')
    conv_dt = []
    for i in range(len(npdt64)):
        conv_dt.append(datetime.fromtimestamp((npdt64[i] - ref_epoch)/np.timedelta64(1, 's'), timezone.utc))
    return conv_dt


# Trim out size-specified borders from data
def trim(data, trim_ratio):
    border_size = math.floor(len(data) * trim_ratio)
    return data[border_size:-border_size]


def synchronize(time_PXI1_LF, RP101SET, time_abs_HBM_LF=None, time_abs_PXI1_LF=None, time_abs_PXI2_HF=None,
                time_abs_PXI2_LF=None, time_HBM_LF=None, CDP_IN=None, CDP_OUT=None, time_PXI2_LF=None,
                VE401=None, PT501=None):
    if PT501 is not None:
        # Set interpolation interval limits #
        left_common = max(time_abs_HBM_LF[0], time_abs_PXI1_LF[0], time_abs_PXI2_HF[0], time_abs_PXI2_LF[0])
        right_common = min(time_abs_HBM_LF[-1], time_abs_PXI1_LF[-1], time_abs_PXI2_HF[-1], time_abs_PXI2_LF[-1])

        # Set interpolation interval (using highest acquisition frequency) #
        interp_time_abs = time_abs_PXI2_HF[time_abs_PXI2_HF > left_common]
        interp_time_abs = interp_time_abs[interp_time_abs < right_common]
        interp_time = [(interp_time_abs[i] - interp_time_abs[0]).total_seconds() for i in range(len(interp_time_abs))]
        interp_time = np.array(interp_time)
        ind_left = np.where(time_abs_PXI2_HF == interp_time_abs[0])[0][0]
        ind_right = np.where(time_abs_PXI2_HF == interp_time_abs[-1])[0][0]

        # Interpolate specific DAQ data to standardize data vector size #
        # HBM_LF
        f_CDP_IN = interp1d(time_HBM_LF, CDP_IN)
        f_CDP_OUT = interp1d(time_HBM_LF, CDP_OUT)
        interp_time_HBM_LF = interp_time + (interp_time_abs[0] - time_abs_HBM_LF[0]).total_seconds()
        CDP_IN_new = f_CDP_IN(interp_time_HBM_LF)
        CDP_OUT_new = f_CDP_OUT(interp_time_HBM_LF)

        # PXI1_LF
        f_RP101SET = interp1d(time_PXI1_LF, RP101SET)
        interp_time_PXI1_LF = interp_time + (interp_time_abs[0] - time_abs_PXI1_LF[0]).total_seconds()
        RP101SET_new = f_RP101SET(interp_time_PXI1_LF)

        # PXI2_LF
        f_VE401 = interp1d(time_PXI2_LF, VE401)
        interp_time_PXI2_LF = interp_time + (interp_time_abs[0] - time_abs_PXI2_LF[0]).total_seconds()
        VE401_new = f_VE401(interp_time_PXI2_LF)

        # PXI2_LF
        PT501_new = PT501[ind_left:ind_right + 1]
    else:
        # For testing purposes, put some placeholder values
        interp_time = time_PXI1_LF[0:1000]
        RP101SET_new = RP101SET[0:1000]
        CDP_IN_new = np.zeros(1000)
        CDP_OUT_new =np.zeros(1000)
        PT501_new = np.zeros(1000)
        VE401_new = np.zeros(1000)

    return interp_time, RP101SET_new, CDP_IN_new, CDP_OUT_new, PT501_new, VE401_new


def main(data_dir_output, files):
    # Set raw data file paths #
    file1, file2, file3, file4 = files

    ###############################
    # Extract data set from files #
    ###############################

    start_time = tm.time()
    HBM_LF = sio.loadmat(file1, squeeze_me=True)
    PXI1_LF = TdmsFile.read(file2).groups()[0]
    PXI2_LF = TdmsFile.read(file3).groups()[0]
    PXI2_HF = TdmsFile.read(file4).groups()[0]
    print("--- Extract data set from files: %.3f seconds ---" % (tm.time() - start_time))

    ######################
    # Transform data set #
    ######################

    # HBM_LF useful channels #
    time_HBM_LF = HBM_LF['Channel_1_Data']
    CDP_IN = HBM_LF['Channel_26_Data']
    CDP_OUT = HBM_LF['Channel_33_Data']
    # sync_HBM_LF = HBM_LF['Channel_16_Data']
    # FS_OUT = HBM_LF['Channel_27_Data']
    # FS_IN = HBM_LF['Channel_28_Data']
    # IMP_OUT = HBM_LF['Channel_29_Data']
    # VOL_Y = HBM_LF['Channel_30_Data']
    # BS_IN = HBM_LF['Channel_31_Data']
    # BS_OUT = HBM_LF['Channel_32_Data']
    # CDP_IN_RED = HBM_LF['Channel_46_Data']
    # VOL_X = HBM_LF['Channel_51_Data']
    # CDP_OUT_RED = HBM_LF['Channel_52_Data']

    # PXI1_LF useful channels #
    time_PXI1_LF = PXI1_LF['System Time'][:]
    time_abs_PXI1_LF = PXI1_LF['Absolute Time'][:]
    RP101SET = PXI1_LF['RP101SET'][:]
    # VCV101_USER = PXI1_LF['VCV101_USER'][:]
    # RP101SET_USER = PXI1_LF['RP101SET_USER'][:]            # -1.0 channel (from another TC)
    # ME401SET_USER = PXI1_LF['ME401SET_USER'][:]
    # ME401SET = PXI1_LF['ME401SET'][:]
    # RP101Feedback = PXI1_LF['RP101Feedback'][:]            # Zero channel
    # RP101ECHO = PXI1_LF['RP101ECHO'][:]                    # Zero channel
    # TT421_2 = PXI1_LF['TT421 2'][:]
    # TT422_2 = PXI1_LF['TT422 2'][:]
    # VCV101 = PXI1_LF['VCV101'][:]
    # MV101D = PXI1_LF['MV101D'][:]
    # MV101F = PXI1_LF['MV101F'][:]
    # MV101T = PXI1_LF['MV101T'][:]
    # temp_GB = PXI1_LF['TTCEMEDIA'][:]
    # MT401J = PXI1_LF['MT401J'][:]
    # MT401S = PXI1_LF['MT401S'][:]
    # MT401T = PXI1_LF['MT401T'][:]
    # MT401X = PXI1_LF['MT401X'][:]
    # FIFO1 = PXI1_LF['FIFO Utilization'][:]
    # Log_Trigger1 = PXI1_LF['Log Trigger'][:]
    # Log_Command1 = PXI1_LF['Log Command'][:]
    # Model_Command1 = PXI1_LF['Model Command'][:]
    # Model_Time1 = PXI1_LF['Model Time'][:]                # Zero channel
    # Model_Status1 = PXI1_LF['Model Status'][:]
    # Inicio1 = PXI1_LF['Inicio'][:]
    # Fim1 = PXI1_LF['Fim'][:]

    # PXI2_LF useful channels #
    time_PXI2_LF = PXI2_LF['System Time'][:]
    time_abs_PXI2_LF = PXI2_LF['Absolute Time'][:]
    VE401 = PXI2_LF['VE401'][:]
    # PR401X_mm = PXI2_LF['PR401X_mm'][:]
    # PR401Y_mm = PXI2_LF['PR401Y_mm'][:]
    # PR402X_mm = PXI2_LF['PR402X_mm'][:]
    # PR402Y_mm = PXI2_LF['PR402Y_mm'][:]
    # PR403X_mm = PXI2_LF['PR403X_mm'][:]
    # PR403Y_mm = PXI2_LF['PR403Y_mm'][:]
    # FIFO2 = PXI2_LF['FIFO Utilization'][:]
    # Log_Trigger2 = PXI2_LF['Log Trigger'][:]
    # Log_Command2 = PXI2_LF['Log Command'][:]
    # Model_Command2 = PXI2_LF['Model Command'][:]
    # Model_Time2 = PXI2_LF['Model Time'][:]
    # Model_Status2 = PXI2_LF['Model Status'][:]
    # Inicio2 = PXI2_LF['Inicio'][:]
    # Fim2 = PXI2_LF['Fim'][:]
    # PT103_offset = PXI2_LF['PT103_offset'][:]                # Noise channel
    # VE402 = PXI2_LF['VE402'][:]
    # VE403 = PXI2_LF['VE403'][:]
    # VE405 = PXI2_LF['VE405'][:]
    # VE406 = PXI2_LF['VE406'][:]
    # VE407 = PXI2_LF['VE407'][:]

    # PXI2_HF useful channels #
    time_PXI2_HF = PXI2_HF['ai7'].time_track()
    time_abs_PXI2_HF = PXI2_HF['ai7'].time_track(absolute_time=True)
    PT501 = 5*PXI2_HF['ai7'][:]
    # acc_GB_x = PXI2_HF['ai0'][:]
    # acc_GB_y = PXI2_HF['ai1'][:]
    # acc_GB_z = PXI2_HF['ai2'][:]
    # acc_CDP_x = PXI2_HF['ai4'][:]
    # acc_CDP_y = PXI2_HF['ai5'][:]
    # acc_CDP_z = PXI2_HF['ai6'][:]
    # prox1_x = -0.127065*PXI2_HF['ai8'][:]
    # prox1_y = -0.127065*PXI2_HF['ai9'][:]
    # prox2_x = -0.127065*PXI2_HF['ai10'][:]
    # prox2_y = -0.127065*PXI2_HF['ai11'][:]
    # prox3_x = -0.127065*PXI2_HF['ai12'][:]
    # prox3_y = -0.127065*PXI2_HF['ai13'][:]

    # Trim out the borders to avoid spurious values #
    trim_factor = 0.05
    time_HBM_LF = trim(time_HBM_LF, trim_factor)
    time_PXI1_LF = trim(time_PXI1_LF, trim_factor)
    time_PXI2_LF = trim(time_PXI2_LF, trim_factor)
    time_PXI2_HF = trim(time_PXI2_HF, trim_factor)
    time_abs_PXI1_LF = trim(time_abs_PXI1_LF, trim_factor)
    time_abs_PXI2_LF = trim(time_abs_PXI2_LF, trim_factor)
    time_abs_PXI2_HF = trim(time_abs_PXI2_HF, trim_factor)
    RP101SET = trim(RP101SET, trim_factor)
    CDP_IN = trim(CDP_IN, trim_factor)
    CDP_OUT = trim(CDP_OUT, trim_factor)
    VE401 = trim(VE401, trim_factor)
    PT501 = trim(PT501, trim_factor)

    # Transform absolute time #
    start_time = tm.time()
    time_abs_PXI1_LF = np.array(convert_from_ts(time_abs_PXI1_LF))
    time_abs_PXI2_LF = np.array(convert_from_ts(time_abs_PXI2_LF))
    time_abs_PXI2_HF = np.array(convert_from_npdt64(time_abs_PXI2_HF))
    print("--- Transform absolute time: %.3f seconds ---" % (tm.time() - start_time))

    # Define relative time #
    time_PXI1_LF = [(time_abs_PXI1_LF[i] - time_abs_PXI1_LF[0]).total_seconds() for i in range(len(time_abs_PXI1_LF))]
    time_PXI2_LF = [(time_abs_PXI2_LF[i] - time_abs_PXI2_LF[0]).total_seconds() for i in range(len(time_abs_PXI2_LF))]
    time_PXI2_HF = [(time_abs_PXI2_HF[i] - time_abs_PXI2_HF[0]).total_seconds() for i in range(len(time_abs_PXI2_HF))]

    # Create absolute time for HBM DAQ based on the measurement delay (different DAQ's) of a given event #
    pass
    time_abs_event = time_abs_PXI1_LF[0]
    time_abs_HBM_LF_first = time_abs_event - timedelta(seconds=time_HBM_LF[0])
    time_abs_HBM_LF = []
    delta_t = time_HBM_LF[1] - time_HBM_LF[0]
    for i in range(len(time_HBM_LF)):
        time_abs_HBM_LF.append(time_abs_HBM_LF_first + timedelta(seconds=i*delta_t))
    time_abs_HBM_LF = np.array(time_abs_HBM_LF)
    time_HBM_LF = [(time_abs_HBM_LF[i] - time_abs_HBM_LF[0]).total_seconds() for i in range(len(time_abs_HBM_LF))]

    interp_time, RP101SET_new, CDP_IN_new, CDP_OUT_new, PT501_new, VE401_new = synchronize(time_PXI1_LF, RP101SET)

    ##############################################
    # Load preprocessed data into a single file #
    ##############################################

    start_time = tm.time()
    with open(os.path.join(data_dir_output, 'DSapp_Test.csv'), mode='w') as out_file:
        header_row = ['RP101 [bar]', 'CDP_IN [bar]', 'CDP_OUT [bar]', 'PT501 [bar]', 'VE401 [m/s2]']
        out_writer = csv.writer(out_file, delimiter=',')

        out_writer.writerow(header_row)
        for i in range(len(interp_time)):
            str1 = '%.6f' % RP101SET_new[i]
            str2 = '%.6f' % CDP_IN_new[i]
            str3 = '%.6f' % CDP_OUT_new[i]
            str4 = '%.6f' % PT501_new[i]
            str5 = '%.6f' % VE401_new[i]
            out_writer.writerow([str1, str2, str3, str4, str5])
    print("--- Load data into output file: %.3f seconds ---" % (tm.time() - start_time))

#############
# Debugging #
#############

# print('')
# print('Relative time of HBM_LF')
# print(len(time_HBM_LF))
# print(min(time_HBM_LF))
# print(max(time_HBM_LF))
# print(time_abs_HBM_LF[0])
# print(time_abs_HBM_LF[-1])

# print('')
# print('Relative and absolute time of PXI1_LF')
# print(len(time_PXI1_LF))
# print(min(time_PXI1_LF))
# print('{:.3f}'.format(max(time_PXI1_LF)))
# print(time_abs_PXI1_LF[0])
# print(time_abs_PXI1_LF[-1])

# print('')
# print('Relative and absolute time of PXI2_LF')
# print(len(time_PXI2_LF))
# print(min(time_PXI2_LF))
# print('{:.3f}'.format(max(time_PXI2_LF)))
# print(time_abs_PXI2_LF[0])
# print(time_abs_PXI2_LF[-1])

# print('')
# print('Relative and absolute time of PXI2_HF')
# print(len(time_PXI2_HF))
# print(min(time_PXI2_HF))
# print('{:.4f}'.format(max(time_PXI2_HF)))
# print(time_abs_PXI2_HF[0])
# print(time_abs_PXI2_HF[-1])

# print('')
# fig = plt.figure('Debug', figsize = (10, 6), dpi = 80)
# plt.plot(np.diff(time_HBM_LF), color = "red", linewidth = 2, linestyle = "-", label = "HBM")
# plt.plot(np.diff(time_PXI1_LF), color = "green", linewidth = 2, linestyle = "-", label = "PXI1_LF")
# plt.plot(np.diff(time_PXI2_LF), color = "blue", linewidth = 2, linestyle = "-", label = "PXI2_LF")
# plt.plot(np.diff(time_PXI2_HF), color = "magenta", linewidth = 2, linestyle = "-", label = "PXI2_HF")
# plt.legend(loc = 'best')
# plt.grid()
# plt.xlabel("Index")
# plt.ylabel("Delta t [s]")
# plt.savefig(os.path.join(data_dir_output, 'Debug - Delta t'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()

# print('')
# fig = plt.figure('Debug', figsize = (10, 6), dpi = 80)
# plt.plot(time_PXI1_LF, RP101SET, color = "red", linewidth = 2, linestyle = "-", label = "RP101SET")
# plt.plot(time_HBM_LF, CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
# #plt.plot(time_PXI2_HF, PT501, color = "blue", linewidth = 2, linestyle = "-", label = "PT501")
# plt.legend(loc = 'upper left')
# plt.grid()
# plt.xlabel("Time [s]")
# plt.ylabel("Pressure [bar]")
# plt.savefig(os.path.join(data_dir_output, 'Debug'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()

# print('')
# fig = plt.figure('Debug2', figsize = (10, 6), dpi = 80)
# plt.plot(CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
# plt.legend(loc = 'upper left')
# plt.grid()
# plt.xlabel("Index [-]")
# plt.ylabel("Pressure [bar]")
# plt.savefig(os.path.join(data_dir_output, 'Debug'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()

# Print data channels names #
# for k in HBM_LF.keys():
#     if 'Channel' in k and 'Header' in k:
#         print('{}: {}'.format(k.replace('Header','Data'), HBM_LF[k]['SignalName']))

# for channel in PXI1_LF.channels():
#     print(channel.name)

# for channel in PXI2_LF.channels():
#     print(channel.name)

# for channel in PXI2_HF.channels():
#     print(channel.name)

# # Print data channels basic properties #
# print('')
# print("** HBM_LF **")
# print(HBM_LF['__header__'])
# print(HBM_LF['__version__'])
# print(HBM_LF['__globals__'])

# print('')
# print("** PXI1_LF **")
# for name, value in PXI1_LF['System Time'].properties.items():
#     print("{0}: {1}".format(name, value))

# print('')
# print("** PXI2_LF **")
# for name, value in PXI2_LF['Absolute Time'].properties.items():
#     print("{0}: {1}".format(name, value))

# print('')
# print("** PXI2_HF **")
# for name, value in PXI2_HF['ai0'].properties.items():
#     print("{0}: {1}".format(name, value))

# # Print data files basic properties #
# print('')
# print("** HBM_LF **")
# print(HBM_LF['File_Header'])
# print(HBM_LF['File_Header'].dtype)

# print('')
# print("** PXI1_LF **")
# for name, value in PXI1_LF.properties.items():
#     print("{0}: {1}".format(name, value))

# print('')
# print("** PXI2_LF **")
# for name, value in PXI2_LF.properties.items():
#     print("{0}: {1}".format(name, value))

# print('')
# print("**PXI2_HF**")
# for name, value in PXI2_HF.properties.items():
#     print("{0}: {1}".format(name, value))

# # Print plateaus debug
# print('')
# print('Original plateaus')
# print('Plateau RP101SET: ({}, {}) - max: {:.3f} - tau: {:.3f} - plat_time = {:.3f}s'.format(plateau_l_1, plateau_r_1, max_1, tau_1, plateau_time_1))
# print('Plateau CDP_IN: ({}, {}) - max: {:.3f} - tau: {:.3f} - plat_time = {:.3f}s'.format(plateau_l_2, plateau_r_2, max_2, tau_2, plateau_time_2))

# print('')
# fig = plt.figure('Original Plateaus', figsize = (10, 6), dpi = 80)
# plt.plot(time_PXI1_LF, RP101SET, color = "red", linewidth = 2, linestyle = "-", label = "RP101SET")
# plt.plot(time_HBM_LF, CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
# plt.axvline(time_PXI1_LF[plateau_l_1], color = 'lightcoral', linestyle = '-.', label = 'Left plateau of RP101SET')
# plt.axvline(time_PXI1_LF[plateau_r_1], color = 'darkred', linestyle = '-.', label = 'Right plateau of RP101SET')
# plt.axvline(time_HBM_LF[plateau_l_2], color = 'lightgreen', linestyle = '-.', label = 'Left plateau of CDP_IN')
# plt.axvline(time_HBM_LF[plateau_r_2], color = 'darkgreen', linestyle = '-.', label = 'Right plateau of CDP_IN')
# plt.legend(loc = 'best')
# plt.grid()
# plt.xlabel("Time [s]")
# plt.ylabel("Pressure [bar]")
# plt.savefig(os.path.join(data_dir_output, 'Original Plateaus'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')

# print('')
# fig = plt.figure('Trimmed Plateaus', figsize = (10, 6), dpi = 80)
# plt.plot(time_PXI1_LF, RP101SET, color = "red", linewidth = 2, linestyle = "-", label = "RP101SET")
# plt.plot(time_HBM_LF, CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
# plt.axvline(time_plat_l_1, color = 'lightcoral', linestyle = '-.', label = 'Left plateau of RP101SET')
# plt.axvline(time_plat_r_1, color = 'darkred', linestyle = '-.', label = 'Right plateau of RP101SET')
# plt.axvline(time_plat_l_2, color = 'lightgreen', linestyle = '-.', label = 'Left plateau of CDP_IN')
# plt.axvline(time_plat_r_2, color = 'darkgreen', linestyle = '-.', label = 'Right plateau of CDP_IN')
# plt.legend(loc = 'best')
# plt.grid()
# plt.xlabel("Time [s]")
# plt.ylabel("Pressure [bar]")
# plt.savefig(os.path.join(data_dir_output, 'Trimmed Plateaus'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
