# headers
import numpy as np
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from datetime import datetime
import os.path as osp
import xlrd

# Path to file
path_to_file_1 = '/Users/roncha/pyDev/auto_rep/COMPLETO_10_31_43_AM_16_08_16_P04.tdms'
path_to_file_2 = '/Users/roncha/pyDev/auto_rep/LOx_pump_Rack2_10_31_44_AM_16_08_16_P04.tdms'

# Read the TDMS data
rack_1 = TdmsFile(path_to_file_1)
rack_2 = TdmsFile(path_to_file_2)

# Root objects 
root_object_1 = rack_1.object()
root_object_2 = rack_2.object()

print(root_object_1.property('name'))

# Get date/time information
time_stamp = root_object_1.property("Created")    # this type of object contains all information
TestInfo.dd = time_stamp.strftime("%d")
TestInfo.mmm = time_stamp.strftime("%b")
TestInfo.yyyy = time_stamp.strftime("%Y")
TestInfo.yr = time_stamp.strftime("%y")
TestInfo.ddmmmyyyy = time_stamp.strftime("%d%b%Y")
TestInfo.yyyymmmdd = time_stamp.strftime("%Y-%b-%d")
TestInfo.yyyy_mmm_dd = time_stamp.strftime("%Y_%b_%d")
TestInfo.HH = time_stamp.strftime("%H")
TestInfo.MM = time_stamp.strftime("%M")
TestInfo.SS = time_stamp.strftime("%S")
TestInfo.FFFFFF = time_stamp.strftime("%f")
TestInfo.HHMMSSFFFFFF = time_stamp.strftime("%H_%M_%S_%f")

# Getting Tex information
memopath = getMemotecFormatFilePath(path_to_file_1)
memopath = memopath.replace('\\', '/')					# LaTeX demands '/' as folder separation, even on Windows
TestInfo.memoFormatFileUm = osp.join(memopath, 'memotecFormat.tex')
TestInfo.memoFormatFileDois = osp.join(memopath,'memotecDeParaData.tex')
TestInfo.IAElogoPath = osp.join(memopath, 'logo_IAE.jpg')
path_split = path_to_file_1.rsplit('.', 1)
TestInfo.tdmsNumber = (path_split[0])[-3:-1]
TestInfo.disclaimer = ('Generated automatically in' + datetime.now().strftime('%d %b %Y')
						+ '; manual alteration of this file is STRONGLY discouraged!')

# Get information from .xlsx
xlsx = xlrd.open_workbook(osp.join(memopath, 'TestInformation.xlsx'))
sheet = xlsx.sheet_by_index(0)			# First sheet

header = sheet.row(0)
header_value = [header[i].value for i in np.arange(len(header))]
if ['Test Day', 'TDMS name', 'Procedure',  'PI', 'PF', 'MMOTEC Number', 'FID Number', 'Code Final Number'] == header_value:
    indRow = 1
    while int(sheet.cell(indRow, 0).value) + 693594 != time_stamp.toordinal() | 		# 1900 jan 1 - Excel's date 1
				TestInfo.tdmsNumber != sheet.cell(indRow, 1).value:						# Care with P1 and P01
        indRow += 1
    TestInfo.procNumber = str(sheet.cell(indRow, 2).value)
    TestInfo.PXX = str(sheet.cell(indRow, 3).value)
    TestInfo.PYY = str(sheet.cell(indRow, 4).value)
    TestInfo.mmotecnum = str(sheet.cell(indRow, 5).value,'%.3d');              # YYY do FID
    TestInfo.FIDNumber = str(sheet.cell(indRow, 6).value)     				   # Z do FID
    TestInfo.codefinalNumber = str(sheet.cell(indRow, 7), '%.3d')              # XXX do FID
else:
    print('Make sure TestInformation.xlsx file is correct!')
TestInfo.memoCode = TestInfo.yyyy_mmm_dd + '_' + TestInfo.HHMMSSFFF

###################################################################################################
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
########################################################################################

def getMemotecFormatFilePath(TDMSfilepath):
	if osp.exists(osp.join(osp.dirname(TDMSfilepath), 'memotecFormat.tex')):
		return osp.dirname(TDMSfilepath)
	elif osp.exists(osp.join(osp.dirname(osp.dirname(TDMSfilepath)), 'memotecFormat.tex')):
		return osp.dirname(osp.dirname(TDMSfilepath))
	else:
		print('There is no memotecFormat.tex!')
		return
