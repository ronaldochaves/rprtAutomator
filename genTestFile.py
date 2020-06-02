# Headers #
import numpy as np
import matplotlib.pyplot as plt
from nptdms import TdmsFile, TdmsGroup, TdmsChannel
from datetime import datetime
import os
import os.path as osp
import scipy.io as sio
import time

# Set raw data file names #
raw_data_dir = osp.join(os.environ['HOME'], 'Desktop')
file1_name = 'cav_trans_P03_4_2018_11_07_13_57_02_1200Hz.MAT'
file2_name = 'Turbine_Rack01_2018_11_07_13_57_02.tdms'
file3_name = 'Turbine_Rack02_2018_11_07_13_57_02.tdms'
file4_name = 'R02S06_PXIe-4499_07-11-2018_13-57-02.tdms'

# Set raw data file paths #
file1 = osp.join(raw_data_dir, file1_name)
file2 = osp.join(raw_data_dir, file2_name)
file3 = osp.join(raw_data_dir, file3_name)
file4 = osp.join(raw_data_dir, file4_name)

start_time = time.time()

# Read data from files #
HBM_LF = sio.loadmat(file1, squeeze_me = True)
PXI1_LF = TdmsFile.read(file2).groups()[0]
PXI2_LF = TdmsFile.read(file3).groups()[0]
PXI2_HF = TdmsFile.read(file4).groups()[0]

print("--- Elapsed time to read data files: %.3f seconds ---" %(time.time() - start_time))

# Print data files basic properties #
print("HBM_LF")
print(HBM_LF['File_Header'])

print("PXI1_LF")
for name, value in PXI1_LF.properties.items():
	print("{0}: {1}".format(name, value))

print("PXI2_LF")
for name, value in PXI2_LF.properties.items():
	print("{0}: {1}".format(name, value))

print("PXI2_HF")
for name, value in PXI2_HF.properties.items():
	print("{0}: {1}".format(name, value))

# Get the data from main (useful) HBM_LF channels #
for k in HBM_LF.keys():
	if 'Channel' in k and 'Header' in k:
		print('{}: {}'.format(k.replace('Header','Data'), HBM_LF[k]['SignalName']))

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
for channel in PXI1_LF.channels():
	print(channel.name)

time_PXI1_LF = PXI1_LF['System Time']
time_abs_PXI1_LF = PXI1_LF['Absolute Time']
VCV101_USER = PXI1_LF['VCV101_USER']
RP101SET_USER = PXI1_LF['RP101SET_USER']
ME401SET_USER = PXI1_LF['ME401SET_USER']
ME401SET = PXI1_LF['ME401SET']
RP101Feedback = PXI1_LF['RP101Feedback']
RP101ECHO = PXI1_LF['RP101ECHO']
RP101SET = PXI1_LF['RP101SET']
TT421_2 = PXI1_LF['TT421 2']
TT422_2 = PXI1_LF['TT422 2']
VCV101 = PXI1_LF['VCV101']
MV101D = PXI1_LF['MV101D']
MV101F = PXI1_LF['MV101F']
MV101T = PXI1_LF['MV101T']
temp_GB = PXI1_LF['TTCEMEDIA']
MT401J = PXI1_LF['MT401J']
MT401S = PXI1_LF['MT401S']
MT401T = PXI1_LF['MT401T']
MT401X = PXI1_LF['MT401X']
FIFO1 = PXI1_LF['FIFO Utilization']
Log_Trigger1 = PXI1_LF['Log Trigger']
Log_Command1 = PXI1_LF['Log Command']
Model_Command1 = PXI1_LF['Model Command']
Model_Time1 = PXI1_LF['Model Time']
Model_Status1 = PXI1_LF['Model Status']
Inicio1 = PXI1_LF['Inicio']
Fim1 = PXI1_LF['Fim']

# Get the data from main (useful) PXI2_LF channels #
for channel in PXI2_LF.channels():
	print(channel.name)

time_PXI2_LF = PXI2_LF['System Time']
time_abs_PXI2_LF = PXI2_LF['Absolute Time']
PR401X_mm = PXI2_LF['PR401X_mm']
PR401Y_mm = PXI2_LF['PR401Y_mm']
PR402X_mm = PXI2_LF['PR402X_mm']
PR402Y_mm = PXI2_LF['PR402Y_mm']
PR403X_mm = PXI2_LF['PR403X_mm']
PR403Y_mm = PXI2_LF['PR403Y_mm']
FIFO2 = PXI2_LF['FIFO Utilization']
Log_Trigger2 = PXI2_LF['Log Trigger']
Log_Command2 = PXI2_LF['Log Command']
Model_Command2 = PXI2_LF['Model Command']
Model_Time2 = PXI2_LF['Model Time']
Model_Status2 = PXI2_LF['Model Status']
Inicio2 = PXI2_LF['Inicio']
Fim2 = PXI2_LF['Fim']
PT103_offset = PXI2_LF['PT103_offset']
VE_401 = PXI2_LF['VE_401']
VE_402 = PXI2_LF['VE_402']
VE_403 = PXI2_LF['VE_403']
VE_405 = PXI2_LF['VE_405']
VE_406 = PXI2_LF['VE_406']
VE_407 = PXI2_LF['VE_407']

# Get the data from main (useful) PXI2_HF channels #
for channel in PXI2_HF.channels():
	print(channel.name)

acc_GB_x = PXI2_HF['ai0']
acc_GB_y = PXI2_HF['ai1']
acc_GB_z = PXI2_HF['ai2']
acc_CDP_x = PXI2_HF['ai4']
acc_CDP_y = PXI2_HF['ai5']
acc_CDP_z = PXI2_HF['ai6']
PT501 = 5*PXI2_HF['ai7']
prox1_x = -0.127065*PXI2_HF['ai8']
prox1_y = -0.127065*PXI2_HF['ai9']
prox2_x = -0.127065*PXI2_HF['ai10']
prox2_y = -0.127065*PXI2_HF['ai11']
prox3_x = -0.127065*PXI2_HF['ai12']
prox3_y = -0.127065*PXI2_HF['ai13']

# Debugging #
print (len(time_HBM_LF))
print (len(time_PXI1_LF))
print (min(time_PXI1_LF))
print (max(time_PXI1_LF))
print (len(time_PXI2_LF))
print (min(time_PXI2_LF))
print (max(time_PXI2_LF))
print (len(acc_GB_x))

# Interpolating data to standardize channels size #
