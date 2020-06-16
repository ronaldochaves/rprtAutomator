# Headers #
import numpy as np
import matplotlib.pyplot as plt
from nptdms import TdmsFile, TdmsGroup, TdmsChannel
from datetime import datetime, date, time, timezone, timedelta
from plateaux import find_plateau
import os
import os.path as osp
import scipy.io as sio
import time
import csv 
import math
from scipy.interpolate import interp1d

# Globals
NI_epoch = datetime(1904, 1, 1, tzinfo = timezone.utc)
sys_epoch = time.gmtime(0)

# Convert epoch-based absolute timestamp (in seconds) from .tdms
def convert_fromTS(ts):
	ref_epoch = datetime(sys_epoch.tm_year, sys_epoch.tm_mon, sys_epoch.tm_mday, tzinfo = timezone.utc)
	conv_dt = []
	for i in range(len(ts)):
		conv_dt.append(ref_epoch + timedelta(seconds = ts[i] + NI_epoch.timestamp()))
	return conv_dt

# Convert epoch-based absolute numpy.datetime64 from .tdms
def convert_fromNPDT64(npdt64):
	ref_epoch = np.datetime64(str(sys_epoch.tm_year) + '-' + str(sys_epoch.tm_mon).zfill(2) + '-' + str(sys_epoch.tm_mday).zfill(2) + 'T00:00:00')
	conv_dt = []
	for i in range(len(npdt64)):
		conv_dt.append(datetime.utcfromtimestamp((npdt64[i] - ref_epoch)/np.timedelta64(1, 's')))
	return conv_dt

# Trim out size-specified borders from data
def trim(data, trim_factor):
	border_size = math.floor(len(data) * trim_factor)
	return data[border_size:-border_size] 

# Set raw data file names #
input_data_dir = osp.join(osp.dirname(os.path.abspath(__file__)), 'input_data')
output_data_dir = osp.join(osp.dirname(os.path.abspath(__file__)), 'output_data')
file1_name = 'cav_P03_5_2018_11_08_15_45_49_1200Hz.MAT'
file2_name = 'Turbine_Rack01_2018_11_08_15_45_48.tdms'
file3_name = 'Turbine_Rack02_2018_11_08_15_45_49.tdms'
file4_name = 'R02S06_PXIe-4499_08-11-2018_15-45-49.tdms'
# file1_name = 'cav_trans_P03_4_2018_11_07_13_57_02_1200Hz.MAT'
# file2_name = 'Turbine_Rack01_2018_11_07_13_57_02.tdms'
# file3_name = 'Turbine_Rack02_2018_11_07_13_57_02.tdms'
# file4_name = 'R02S06_PXIe-4499_07-11-2018_13-57-02.tdms'
# file1_name = 'cav_trans_P03_7_2018_11_08_15_56_09_1200Hz.MAT'
# file2_name = 'Turbine_Rack01_2018_11_08_15_56_08.tdms'
# file3_name = 'Turbine_Rack02_2018_11_08_15_56_09.tdms'
# file4_name = 'R02S06_PXIe-4499_08-11-2018_15-56-09.tdms'

# Set raw data file paths #
file1 = osp.join(input_data_dir, file1_name)
file2 = osp.join(input_data_dir, file2_name)
file3 = osp.join(input_data_dir, file3_name)
file4 = osp.join(input_data_dir, file4_name)

start_time = time.time()

# Read data from files #
HBM_LF = sio.loadmat(file1, squeeze_me = True)
PXI1_LF = TdmsFile.read(file2).groups()[0]
PXI2_LF = TdmsFile.read(file3).groups()[0]
PXI2_HF = TdmsFile.read(file4).groups()[0]

print("--- Elapsed time to read data files: %.3f seconds ---" %(time.time() - start_time))

# Get the data from main (useful) HBM_LF channels #
time_HBM_LF = HBM_LF['Channel_1_Data']
sync_HBM_LF = HBM_LF['Channel_16_Data']
CDP_IN = HBM_LF['Channel_26_Data']
FS_OUT = HBM_LF['Channel_27_Data']
FS_IN = HBM_LF['Channel_28_Data']
IMP_OUT = HBM_LF['Channel_29_Data']
VOL_Y = HBM_LF['Channel_30_Data']
BS_IN = HBM_LF['Channel_31_Data']
BS_OUT = HBM_LF['Channel_32_Data']
CDP_OUT = HBM_LF['Channel_33_Data']
CDP_IN_RED = HBM_LF['Channel_46_Data']
VOL_X = HBM_LF['Channel_51_Data']
CDP_OUT_RED = HBM_LF['Channel_52_Data']

# Get the data from main (useful) PXI1_LF channels #
time_PXI1_LF = PXI1_LF['System Time'][:]
time_abs_PXI1_LF = PXI1_LF['Absolute Time'][:]
VCV101_USER = PXI1_LF['VCV101_USER'][:]
RP101SET_USER = PXI1_LF['RP101SET_USER'][:]			# -1.0 channel (from another TC)
ME401SET_USER = PXI1_LF['ME401SET_USER'][:]
ME401SET = PXI1_LF['ME401SET'][:]
RP101Feedback = PXI1_LF['RP101Feedback'][:]			# Zero channel
RP101ECHO = PXI1_LF['RP101ECHO'][:]					# Zero channel
RP101SET = PXI1_LF['RP101SET'][:]
TT421_2 = PXI1_LF['TT421 2'][:]
TT422_2 = PXI1_LF['TT422 2'][:]
VCV101 = PXI1_LF['VCV101'][:]
MV101D = PXI1_LF['MV101D'][:]
MV101F = PXI1_LF['MV101F'][:]
MV101T = PXI1_LF['MV101T'][:]
temp_GB = PXI1_LF['TTCEMEDIA'][:]
MT401J = PXI1_LF['MT401J'][:]
MT401S = PXI1_LF['MT401S'][:]
MT401T = PXI1_LF['MT401T'][:]
MT401X = PXI1_LF['MT401X'][:]
FIFO1 = PXI1_LF['FIFO Utilization'][:]
Log_Trigger1 = PXI1_LF['Log Trigger'][:]
Log_Command1 = PXI1_LF['Log Command'][:]
Model_Command1 = PXI1_LF['Model Command'][:]
Model_Time1 = PXI1_LF['Model Time'][:]				# Zero channel
Model_Status1 = PXI1_LF['Model Status'][:]
Inicio1 = PXI1_LF['Inicio'][:]
Fim1 = PXI1_LF['Fim'][:]

# Get the data from main (useful) PXI2_LF channels #
time_PXI2_LF = PXI2_LF['System Time'][:]
time_abs_PXI2_LF = PXI2_LF['Absolute Time'][:]
PR401X_mm = PXI2_LF['PR401X_mm'][:]
PR401Y_mm = PXI2_LF['PR401Y_mm'][:]
PR402X_mm = PXI2_LF['PR402X_mm'][:]
PR402Y_mm = PXI2_LF['PR402Y_mm'][:]
PR403X_mm = PXI2_LF['PR403X_mm'][:]
PR403Y_mm = PXI2_LF['PR403Y_mm'][:]
FIFO2 = PXI2_LF['FIFO Utilization'][:]
Log_Trigger2 = PXI2_LF['Log Trigger'][:]
Log_Command2 = PXI2_LF['Log Command'][:]
Model_Command2 = PXI2_LF['Model Command'][:]
Model_Time2 = PXI2_LF['Model Time'][:]
Model_Status2 = PXI2_LF['Model Status'][:]
Inicio2 = PXI2_LF['Inicio'][:]
Fim2 = PXI2_LF['Fim'][:]
PT103_offset = PXI2_LF['PT103_offset'][:]				# Noise channel
VE401 = PXI2_LF['VE401'][:]
VE402 = PXI2_LF['VE402'][:]
VE403 = PXI2_LF['VE403'][:]
VE405 = PXI2_LF['VE405'][:]
VE406 = PXI2_LF['VE406'][:]
VE407 = PXI2_LF['VE407'][:]

# Get the data from main (useful) PXI2_HF channels #
time_PXI2_HF = PXI2_HF['ai0'].time_track()
time_abs_PXI2_HF = PXI2_HF['ai0'].time_track(absolute_time = True)
acc_GB_x = PXI2_HF['ai0'][:]
acc_GB_y = PXI2_HF['ai1'][:]
acc_GB_z = PXI2_HF['ai2'][:]
acc_CDP_x = PXI2_HF['ai4'][:]
acc_CDP_y = PXI2_HF['ai5'][:]
acc_CDP_z = PXI2_HF['ai6'][:]
PT501 = 5*PXI2_HF['ai7'][:]
prox1_x = -0.127065*PXI2_HF['ai8'][:]
prox1_y = -0.127065*PXI2_HF['ai9'][:]
prox2_x = -0.127065*PXI2_HF['ai10'][:]
prox2_y = -0.127065*PXI2_HF['ai11'][:]
prox3_x = -0.127065*PXI2_HF['ai12'][:]
prox3_y = -0.127065*PXI2_HF['ai13'][:]

# Trimming out the borders to avoid spurious values #
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

# Shifting relative time (first element to be zero) and adjusting absolute time #
time_HBM_LF = time_HBM_LF - time_HBM_LF[0]
time_PXI1_LF = time_PXI1_LF - time_PXI1_LF[0]
time_PXI2_LF = time_PXI2_LF - time_PXI2_LF[0]
time_PXI2_HF = time_PXI2_HF - time_PXI2_HF[0]

start_time = time.time()
time_abs_PXI1_LF = convert_fromTS(time_abs_PXI1_LF)
time_abs_PXI2_LF = convert_fromTS(time_abs_PXI2_LF)
time_abs_PXI2_HF = convert_fromNPDT64(time_abs_PXI2_HF)
print("--- Elapsed time to convert absolute time vectors: %.3f seconds ---" %(time.time() - start_time))

# Find plateaus from data of different DAQ's #
plateau_l_1, plateau_r_1, m_1, tau_1 = find_plateau(RP101SET, 0.1)
plateau_time_1 = (plateau_r_1 - plateau_l_1)/1000
max_1 = RP101SET[m_1]
plateau_l_2, plateau_r_2, m_2, tau_2 = find_plateau(CDP_IN, 0.15, uncert = 5e-2)
plateau_time_2 = (plateau_r_2 - plateau_l_2)/1200
max_2 = CDP_IN[m_2]

print('')
fig = plt.figure('Original Plateaus', figsize = (10, 6), dpi = 80)
plt.plot(time_PXI1_LF, RP101SET, color = "red", linewidth = 2, linestyle = "-", label = "RP101SET")
plt.plot(time_HBM_LF, CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
plt.axvline(time_PXI1_LF[plateau_l_1], color = 'lightcoral', linestyle = '-.', label = 'Left plateau of RP101SET')
plt.axvline(time_PXI1_LF[plateau_r_1], color = 'darkred', linestyle = '-.', label = 'Right plateau of RP101SET')
plt.axvline(time_HBM_LF[plateau_l_2], color = 'lightgreen', linestyle = '-.', label = 'Left plateau of CDP_IN')
plt.axvline(time_HBM_LF[plateau_r_2], color = 'darkgreen', linestyle = '-.', label = 'Right plateau of CDP_IN')
plt.legend(loc = 'best')
plt.grid()
plt.xlabel("Time [s]")
plt.ylabel("Pressure [bar]")
plt.savefig(osp.join(output_data_dir, 'Original Plateaus'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
plt.show()

# Synchronize different DAQ's by shifting (sliding) data in relation to each other (time lag) #
pass

time_lag = 0		# time_HBM_LF - time_PXI1_LF [s]
if time_lag >= 0:
	ind_l = math.floor(time_lag*1200)
	print(ind_l)
else:
	print('Error: Events happen first in PXI than in HBM!')

time_plat_l_2 = time_HBM_LF[plateau_l_2] - time_lag
time_plat_r_2 = time_HBM_LF[plateau_r_2] - time_lag
time_plat_l_1 = time_PXI1_LF[plateau_l_1]
time_plat_r_1 = time_PXI1_LF[plateau_r_1]

if time_HBM_LF[-1 - ind_l] >= time_PXI1_LF[-1]:
	ind_r = math.floor((time_HBM_LF[-1 - ind_l] - time_PXI1_LF[-1])*1200)
	print(ind_r)
	time_plat_r_2 = time_plat_r_2 - (time_HBM_LF[-1 - ind_l] - time_PXI1_LF[-1])
	time_HBM_LF = time_HBM_LF[ind_l:-1 - ind_r]
	CDP_IN = CDP_IN[ind_l:-1 - ind_r]
else:
	ind_r = math.floor((time_PXI1_LF[-1] - time_HBM_LF[-1 - ind_l])*1000)
	print(ind_r)
	time_plat_r_1 = time_plat_r_1 - (time_PXI1_LF[-1] - time_HBM_LF[-1 - ind_l])
	time_HBM_LF = time_HBM_LF[ind_l:]
	CDP_IN = CDP_IN[ind_l:]
	time_PXI1_LF = time_PXI1_LF[:-1 - ind_r]
	RP101SET = RP101SET[:-1 - ind_r]
time_HBM_LF = time_HBM_LF - time_HBM_LF[0]

# # Interpolating data to standardize data vector size #
# f_CDP_IN = interp1d(time_HBM_LF, CDP_IN)
# CDP_IN_new = f_CDP_IN(time_PXI2_HF)
# f_RP101SET = interp1d(time_PXI1_LF, RP101SET)
# RP101SET_new = f_RP101SET(time_PXI2_HF)
# print(len(CDP_IN_new))
# print(len(RP101SET_new))
# print(len(time_PXI2_HF))

# Export all information in a single file #
#with open(osp.join(output_data_dir, 'DSapp_Test.csv'), mode = 'w') as csv_file:
#	fieldnames = ['RP101', 'CDP_IN', 'CDP_OUT', 'PT501', 'VE401']
#	writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
#	writer.writeheader()
#	for i in range(len(VE401)):
#		writer.writerow('RP101':str(RP101SET[i]), 'CDP_IN':str(CDP_IN[i]), 'CDP_OUT':str(CDP_OUT[i]), 'PT501':str(PT501[i]), 'VE401':str(VE401[i]))

# Debugging #
print('')
print('Relative time of HBM_LF')
print(len(time_HBM_LF))
print(min(time_HBM_LF))
print(max(time_HBM_LF))

print('')
print('Relative and absolute time of PXI1_LF')
print(len(time_PXI1_LF))
print(min(time_PXI1_LF))
print(max(time_PXI1_LF))
print(time_abs_PXI1_LF[0])
print(time_abs_PXI1_LF[-1])

print('')
print('Relative and absolute time of PXI2_LF')
print(len(time_PXI2_LF))
print(min(time_PXI2_LF))
print(max(time_PXI2_LF))
print(time_abs_PXI2_LF[0])
print(time_abs_PXI2_LF[-1])

print('')
print('Relative and absolute time of PXI2_HF')
print(len(time_PXI2_HF))
print(min(time_PXI2_HF))
print(max(time_PXI2_HF))
print(time_abs_PXI2_HF[0])
print(time_abs_PXI2_HF[-1])

# print('')
# fig = plt.figure('Debug', figsize = (10, 6), dpi = 80)
# plt.plot(time_PXI1_LF, RP101SET, color = "red", linewidth = 2, linestyle = "-", label = "RP101SET")
# plt.plot(time_HBM_LF, CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
# #plt.plot(time_PXI2_HF, PT501, color = "blue", linewidth = 2, linestyle = "-", label = "PT501")
# plt.legend(loc = 'upper left')
# plt.grid()
# plt.xlabel("Time [s]")
# plt.ylabel("Pressure [bar]")
# plt.savefig(osp.join(output_data_dir, 'Debug'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()

# print('')
# fig = plt.figure('Debug2', figsize = (10, 6), dpi = 80)
# plt.plot(CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
# plt.legend(loc = 'upper left')
# plt.grid()
# plt.xlabel("Index [-]")
# plt.ylabel("Pressure [bar]")
# plt.savefig(osp.join(output_data_dir, 'Debug'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()

# Print data channels names #
for k in HBM_LF.keys():
	if 'Channel' in k and 'Header' in k:
		print('{}: {}'.format(k.replace('Header','Data'), HBM_LF[k]['SignalName']))

for channel in PXI1_LF.channels():
	print(channel.name)

for channel in PXI2_LF.channels():
	print(channel.name)

for channel in PXI2_HF.channels():
	print(channel.name)

# Print data channels basic properties #
print('')
print("** HBM_LF **")
print(HBM_LF['__header__'])
print(HBM_LF['__version__'])
print(HBM_LF['__globals__'])

print('')
print("** PXI1_LF **")
for name, value in PXI1_LF['System Time'].properties.items():
	print("{0}: {1}".format(name, value))

print('')
print("** PXI2_LF **")
for name, value in PXI2_LF['Absolute Time'].properties.items():
	print("{0}: {1}".format(name, value))

print('')
print("** PXI2_HF **")
for name, value in PXI2_HF['ai0'].properties.items():
	print("{0}: {1}".format(name, value))

# Print data files basic properties #
print('')
print("** HBM_LF **")
print(HBM_LF['File_Header'])
print(HBM_LF['File_Header'].dtype)

print('')
print("** PXI1_LF **")
for name, value in PXI1_LF.properties.items():
	print("{0}: {1}".format(name, value))

print('')
print("** PXI2_LF **")
for name, value in PXI2_LF.properties.items():
	print("{0}: {1}".format(name, value))

print('')
print("**PXI2_HF**")
for name, value in PXI2_HF.properties.items():
	print("{0}: {1}".format(name, value))

# Print plateaus debug
print('')
print('Original plateaus')
print('Plateau RP101SET: ({}, {}) - max: {:.3f} - tau: {:.3f} - plat_time = {:.3f}s'.format(plateau_l_1, plateau_r_1, max_1, tau_1, plateau_time_1))
print('Plateau CDP_IN: ({}, {}) - max: {:.3f} - tau: {:.3f} - plat_time = {:.3f}s'.format(plateau_l_2, plateau_r_2, max_2, tau_2, plateau_time_2))

print('')
fig = plt.figure('Trimmed Plateaus', figsize = (10, 6), dpi = 80)
plt.plot(time_PXI1_LF, RP101SET, color = "red", linewidth = 2, linestyle = "-", label = "RP101SET")
plt.plot(time_HBM_LF, CDP_IN, color = "green", linewidth = 2, linestyle = "-", label = "CDP_IN")
plt.axvline(time_plat_l_1, color = 'lightcoral', linestyle = '-.', label = 'Left plateau of RP101SET')
plt.axvline(time_plat_r_1, color = 'darkred', linestyle = '-.', label = 'Right plateau of RP101SET')
plt.axvline(time_plat_l_2, color = 'lightgreen', linestyle = '-.', label = 'Left plateau of CDP_IN')
plt.axvline(time_plat_r_2, color = 'darkgreen', linestyle = '-.', label = 'Right plateau of CDP_IN')
plt.legend(loc = 'best')
plt.grid()
plt.xlabel("Time [s]")
plt.ylabel("Pressure [bar]")
plt.savefig(osp.join(output_data_dir, 'Trimmed Plateaus'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
plt.show()