# headers
import numpy as np
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from datetime import datetime

# Path to file
path_to_file_1 = '/Users/roncha/pyDev/auto_rep/COMPLETO_10_31_43_AM_16_08_16_P04.tdms'
path_to_file_2 = '/Users/roncha/pyDev/auto_rep/LOx_pump_Rack2_10_31_44_AM_16_08_16_P04.tdms'

# Read the TDMS data
rack_1 = TdmsFile(path_to_file_1)
rack_2 = TdmsFile(path_to_file_2)

root_object = rack_1.object()
root_object_2 = rack_2.object()

# Get groups (rack names)                 # automatize in the future
group_names_1 = rack_1.groups()
group_names_2 = rack_2.groups()
print('List of groups of the rack_1 TDMS:', group_names_1[0])
print('List of groups of the rack_2 TDMS:', group_names_2[0])

# Get channel names of the group
if len(group_names_1) == 1:
	channel_names_1 = rack_1.group_channels(group_names_1[0])
if len(group_names_2) == 1:
	channel_names_2 = rack_2.group_channels(group_names_2[0])

# Get the data from channels
PT101 = rack_1.channel_data(group_names_1[0], "PT101")
PT102 = rack_1.channel_data(group_names_1[0], "PT102")
PT103 = rack_2.channel_data(group_names_2[0], "PT103")
PT104 = rack_2.channel_data(group_names_2[0], "PT104")
PT551 = rack_1.channel_data(group_names_1[0], "PT551")
PT552 = rack_1.channel_data(group_names_1[0], "PT552")
PT553 = rack_1.channel_data(group_names_1[0], "PT553")
PT421 = rack_1.channel_data(group_names_1[0], "PT421")
MT401S = rack_1.channel_data(group_names_1[0], "MT401S") 
MT401T = rack_1.channel_data(group_names_1[0], "MT401T")
MT401J = rack_1.channel_data(group_names_1[0], "MT401J")
MV101F = rack_1.channel_data(group_names_1[0], "MV101F")
TTCEMEDIA = rack_1.channel_data(group_names_1[0], "TTCEMEDIA")

# Synchronize relative times from both racks
Time_1 = rack_1.channel_data(group_names_1[0], "System Time")
Time_2 = rack_2.channel_data(group_names_2[0], "System Time")

if Time_1.min() <= Time_2.min():
    indminLOx = 0
    indminTPU = 0
    while Time_1[indminTPU] != Time_2[0]:
        indminTPU += 1
else:
    indminTPU = 0
    indminLOx = 0
    while Time_2[indminLOx] != Time_1[0]:
        indminLOx += 1

if Time_1.max() <= Time_2.max():
    indmaxLOx = len(Time_2) - 1
    indmaxTPU = len(Time_1) - 1
    while Time_2[indmaxLOx] != Time_1[-1]:
        indmaxLOx -= 1
else:
    indmaxLOx = len(Time_2) - 1
    indmaxTPU = len(Time_1) - 1
    while tempoTPU[indmaxTPU] != tempoLOx[-1]:
        indmaxTPU -= 1

Time_1 = Time_1[indminTPU:indmaxTPU]
Time_2 = Time_2[indminLOx:indmaxLOx]
Time_1 = Time_1 - Time_1.min()       # tempoTPU and tempoLOx are equals now and starting from 0
Time_2 = Time_2 - Time_2.min()
Time = Time_1
xLimit = [Time.min(), Time.max()]

# Get date/time information
time_stamp = root_object.property("Created")    # this type of object contains all information
print(time_stamp)
time_stamp_2 = root_object_2.property("Created")    # this type of object contains all information
print(time_stamp_2)
dd = time_stamp.strftime("%d")
mmm = time_stamp.strftime("%b")
yyyy = time_stamp.strftime("%Y")
yr = time_stamp.strftime("%y")
ddmmmyyyy = time_stamp.strftime("%d%b%Y")
yyyymmmdd = time_stamp.strftime("%Y-%b-%d")
yyyy_mmm_dd = time_stamp.strftime("%Y_%b_%d")
HH = time_stamp.strftime("%H")
MM = time_stamp.strftime("%M")
SS = time_stamp.strftime("%S")
FFFFFF = time_stamp.strftime("%f")
HHMMSSFFFFFF = time_stamp.strftime("%H_%M_%S_%f")


########################################################################################
# Plots
fig = plt.figure("Time plots after correction", figsize = (10, 6), dpi = 80)
plt.plot(Time_1, color = "blue", linewidth = 2, linestyle = "-", label = "rack_1 time")
plt.plot(Time_2, color = "red",  linewidth = 2, linestyle = "-", label = "rack_2 time")
plt.legend(loc = 'upper left')
plt.grid()
plt.title("Time from racks")
plt.xlabel("Index")
plt.ylabel("Time [s]")
plt.savefig('times_after_correc', dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()

fig = plt.figure("Basic Plots", figsize = (10, 6), dpi = 80)
plt.plot(Time, PT103[indminLOx:indmaxLOx], color = "blue", linewidth = 2, linestyle = "-", label = "PT103")
plt.plot(Time, PT104[indminLOx:indmaxLOx], color = "red",  linewidth = 2, linestyle = "-", label = "PT104")
plt.legend(loc = 'center left')
plt.grid()
plt.title("Pressure transducer signals")
plt.xlabel("Time [s]")
plt.ylabel("Pressure [bar]")
plt.savefig('Prss', dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()

fig = plt.figure("Torquemeter", figsize = (10, 6), dpi = 80)
plt.plot(Time, MT401T[indminTPU:indmaxTPU], color = "blue", linewidth = 2, linestyle = "-", label = "MT401T")
plt.plot(Time, MT401J[indminTPU:indmaxTPU], color = "red",  linewidth = 2, linestyle = "-", label = "MT401J")
plt.legend(loc = 'lower center')
plt.grid()
plt.title("Pressure transducer signals")
plt.xlabel("Time [s]")
plt.ylabel("Torque [N.m] & Power [kW]")
plt.savefig('Trqm', dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
# plt.show()