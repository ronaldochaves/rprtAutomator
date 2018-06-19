# headers
import numpy as np
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from datetime import datetime
import os.path as osp
import xlrd

# Globals
memoFormatName = 'memotecFormat.tex'
memoDeParaData = 'memotecDeParaData.tex' 
logo = 'logo_IAE.jpg'
TestInfoxlName = 'TestInformation.xlsx'

def getEntryValues(path_to_file_1, path_to_file_2):
    # Read the TDMS data
    rack_1 = TdmsFile(path_to_file_1)
    rack_2 = TdmsFile(path_to_file_2)

    # Root objects 
    root_object_1 = rack_1.object()
    root_object_2 = rack_2.object()

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
    TestInfo.memoCode = TestInfo.yyyy_mmm_dd + '_' + TestInfo.HHMMSSFFFFFF      # Code for generated figures

    # Getting Tex information
    memopath = getMemotecFormatFilePath(path_to_file_1)
    memopath = memopath.replace('\\', '/')					# LaTeX demands '/' as folder separation, even on Windows
    TestInfo.memoFormatFileUm = osp.join(memopath, memoFormatName)
    TestInfo.memoFormatFileDois = osp.join(memopath, memoDeParaData)
    TestInfo.IAElogoPath = osp.join(memopath, logo)
    path_split = path_to_file_1.rsplit('.', 1)
    TestInfo.tdmsNumber = (path_split[0])[-3:-1]            # Point ID on the TDMS file name (it can be improved!)
    TestInfo.disclaimer = ('Generated automatically in' + datetime.now().strftime('%d %b %Y')
    						+ '; manual alteration of this file is STRONGLY discouraged!')

    # Get information from .xlsx
    xlsx = xlrd.open_workbook(osp.join(memopath, TestInfoxlName))
    sheet = xlsx.sheet_by_index(0)			# First sheet
    header = sheet.row_values(0)            # First row

    if ['Test Day', 'TDMS name', 'Procedure',  'PI', 'PF', 'MMOTEC Number', 'FID Number', 'Code Final Number'] == header:
        dates = sheet.col(0)
        tdmsNumbers = sheet.col(1)
        inds = [i for i, x in enumerate(dates) if issameDay(time_stamp, x) & issameTDMS(TestInfo.tdmsNumber, tdmsNumbers[i])]
        indRow = inds[0]

        TestInfo.procNumber = str(int(sheet.cell(indRow, 2).value))
        TestInfo.PXX = str(int(sheet.cell(indRow, 3).value))
        TestInfo.PYY = str(int(sheet.cell(indRow, 4).value))
        TestInfo.mmotecnum = format(int(sheet.cell(indRow, 5).value), '03d')           # YYY do FID
        TestInfo.FIDNumber = str(int(sheet.cell(indRow, 6).value))   				   # Z do FID
        TestInfo.codefinalNumber = format(int(sheet.cell(indRow, 7).value), '03d')     # XXX do FID
    else:
        print('Make sure ' + TestInfoxlName + ' file is correct!')

    ###################################################################################################
    # Get groups (rack names)                 # automatize in the future
    group_names_1 = rack_1.groups()
    group_names_2 = rack_2.groups()

    # Synchronize relative times from both racks
    Time_1 = rack_1.channel_data(group_names_1[0], "System Time")
    Time_2 = rack_2.channel_data(group_names_2[0], "System Time")
    indminLOx, indmaxLOx, indminTPU, indmaxTPU = syncTime(Time_1, Time_2)
    Time = Time_1[indminTPU:indmaxTPU]

    # Get the (really useful) data from channels
    PT101 = (rack_1.channel_data(group_names_1[0], "PT101"))[indminTPU:indmaxTPU]
    PT102 = (rack_1.channel_data(group_names_1[0], "PT102"))[indminTPU:indmaxTPU]
    PT103 = (rack_2.channel_data(group_names_2[0], "PT103"))[indminLOx:indmaxLOx]
    PT104 = (rack_2.channel_data(group_names_2[0], "PT104"))[indminLOx:indmaxLOx]
    PT551 = (rack_1.channel_data(group_names_1[0], "PT551"))[indminTPU:indmaxTPU]
    PT552 = (rack_1.channel_data(group_names_1[0], "PT552"))[indminTPU:indmaxTPU]
    PT553 = (rack_1.channel_data(group_names_1[0], "PT553"))[indminTPU:indmaxTPU]
    PT421 = (rack_1.channel_data(group_names_1[0], "PT421"))[indminTPU:indmaxTPU]
    MT401S = (rack_1.channel_data(group_names_1[0], "MT401S"))[indminTPU:indmaxTPU]
    MT401T = (rack_1.channel_data(group_names_1[0], "MT401T"))[indminTPU:indmaxTPU]
    MT401J = (rack_1.channel_data(group_names_1[0], "MT401J"))[indminTPU:indmaxTPU]
    MV101F = (rack_1.channel_data(group_names_1[0], "MV101F"))[indminTPU:indmaxTPU]
    TTCEMEDIA = (rack_1.channel_data(group_names_1[0], "TTCEMEDIA"))[indminTPU:indmaxTPU]

    ########################################################################################
    # Plots
    fig = plt.figure("Time plots after correction", figsize = (10, 6), dpi = 80)
    plt.plot(Time_1, color = "blue", linewidth = 2, linestyle = "-", label = "rack_1 time")
    plt.plot(Time_2, color = "red",  linewidth = 2, linestyle = "-", label = "rack_2 time")
    plt.legend(loc = 'upper left')
    plt.grid()
    plt.title("Time from racks after Synchronization")
    plt.xlabel("Index")
    plt.ylabel("Time [s]")
    plt.savefig('SyncTime' + TestInfo.memoCode, dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
    # plt.show()

    fig = plt.figure("Basic Plots", figsize = (10, 6), dpi = 80)
    plt.plot(Time, PT103, color = "blue", linewidth = 2, linestyle = "-", label = "PT103")
    plt.plot(Time, PT104, color = "red",  linewidth = 2, linestyle = "-", label = "PT104")
    plt.legend(loc = 'center left')
    plt.grid()
    plt.title("Pressure transducer signals")
    plt.xlabel("Time [s]")
    plt.ylabel("Pressure [bar]")
    plt.savefig('Prss' + TestInfo.memoCode, dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
    # plt.show()

    fig = plt.figure("Torquemeter", figsize = (10, 6), dpi = 80)
    plt.plot(Time, MT401T, color = "blue", linewidth = 2, linestyle = "-", label = "MT401T")
    plt.plot(Time, MT401J, color = "red",  linewidth = 2, linestyle = "-", label = "MT401J")
    plt.legend(loc = 'lower center')
    plt.grid()
    plt.title("Pressure transducer signals")
    plt.xlabel("Time [s]")
    plt.ylabel("Torque [N.m] & Power [kW]")
    plt.savefig('Trqm' + TestInfo.memoCode, dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
    # plt.show()
    ########################################################################################

def getMemotecFormatFilePath(TDMSfilepath):
	if osp.exists(osp.join(osp.dirname(TDMSfilepath), memoFormatName)):
		return osp.dirname(TDMSfilepath)
	elif osp.exists(osp.join(osp.dirname(osp.dirname(TDMSfilepath)), memoFormatName)):
		return osp.dirname(osp.dirname(TDMSfilepath))
	else:
		print('There is no ' + memoFormatName + '!')
		return

# Compare dates from TDMS time stamp and from excel data
def issameDay(date1, date2_cell):
    if date2_cell.ctype == 3:                    # http://xlrd.readthedocs.io/en/latest/api.html#xlrd.sheet.Cell
        if (date1 - xlrd.xldate.xldate_as_datetime(date2_cell.value, 0)).days == 0:
            return True
        else:
            return False
    else:
        return False

# Compare tdmsNumber from TDMS name and from excel data
def issameTDMS(tdmsNumber1, tdmsNumber2_cell):
    if tdmsNumber2_cell.ctype == 1:
            if tdmsNumber2_cell.value == tdmsNumber1:     # It is possible to make code more robust here ('P1' vs 'P01', etc)
            return True
        else:
            return False
    else:
        return False

def syncTime(Time_1, Time_2):
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
    return indminLOx, indmaxLOx, indminTPU, indmaxTPU

# Main function
def getTestInfo(path_to_file_1, path_to_file_2):
    getEntryValues(path_to_file_1, path_to_file_2)
    pass

if __name__ == '__main__':                      # Execute test case
    # Path to file
    path_to_file_1 = '/Users/roncha/pyDev/auto_rep/COMPLETO_10_31_43_AM_16_08_16_P04.tdms'
    path_to_file_2 = '/Users/roncha/pyDev/auto_rep/LOx_pump_Rack2_10_31_44_AM_16_08_16_P04.tdms'
    getTestInfo(path_to_file_1, path_to_file_2)