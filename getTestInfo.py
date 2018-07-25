# headers
import numpy as np
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from datetime import datetime, date
import os.path as osp
import xlrd
from scipy.signal import butter, filtfilt, sosfiltfilt

# Globals
memoFormatName = 'memotecFormat.tex'
memoDeParaData = 'memotecDeParaData.tex' 
logoName = 'logo_IAE.jpg'
TestInfoxlName = 'TestInformation.xlsx'

class testInfo(dict):                           # http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self

    # Get date/time info to be used in the report generation
    def add_datetime_strs(self):
        rack_1 = TdmsFile(self.file_1)
        root_object_1 = rack_1.object()
        time_stamp = root_object_1.property("Created")    # this object contains all date/time information
        self.time_stamp = time_stamp
        self.dd = time_stamp.strftime("%d")
        self.mmm = time_stamp.strftime("%b")
        self.yyyy = time_stamp.strftime("%Y")
        self.yr = time_stamp.strftime("%y")
        self.ddmmmyyyy = time_stamp.strftime("%d%b%Y")
        self.yyyymmmdd = time_stamp.strftime("%Y-%b-%d")
        self.yyyy_mmm_dd = time_stamp.strftime("%Y_%b_%d")
        self.HH = time_stamp.strftime("%H")
        self.MM = time_stamp.strftime("%M")
        self.SS = time_stamp.strftime("%S")
        self.FFFFFF = time_stamp.strftime("%f")
        self.HHMMSS = time_stamp.strftime("%H:%M:%S")
        # self.HHMMSSFFF = time_stamp.strftime("%H_%M_%S_%3f")
        self.HHMMSSFFFFFF = time_stamp.strftime("%H_%M_%S_%f")
        self.memoCode = self.yyyy_mmm_dd + '_' + self.HHMMSSFFFFFF      # Code for generated figures

    # Add basic information from tex templates
    def add_tex_info(self, templateNames):
        memoFormat, memoDeParaData, logo = templateNames
        memopath = getMemotecFormatFilePath(self.file_1)
        memopath = memopath.replace('\\', '/')                  # LaTeX demands '/' as folder separation, even on Windows
        self.memopath = memopath
        self.memoFormatFileUm = osp.join(self.memopath, memoFormat)
        self.memoFormatFileDois = osp.join(memopath, memoDeParaData)
        self.IAElogoPath = osp.join(memopath, logo)
        path_split = self.file_1.rsplit('.', 1)
        self.tdmsNumber = (path_split[0])[-3:-1]                # Point ID on the TDMS file name (it can be improved!)
        self.disclaimer = ('Generated automatically in ' + datetime.now().strftime('%d %b %Y') 
            + '; manual alteration of this file is STRONGLY discouraged!')

    # Add basic information from XL campaign file
    def add_xl_info(self, xlName):
        xlsx = xlrd.open_workbook(osp.join(self.memopath, xlName))
        sheet = xlsx.sheet_by_index(0)			# First sheet
        header = sheet.row_values(0)            # First row

        if ['Test Day', 'TDMS name', 'Procedure',  'PI', 'PF', 'MMOTEC Number', 'FID Number', 'Code Final Number'] == header:
            dates = sheet.col(0)
            tdmsNumbers = sheet.col(1)
            inds = [i for i, x in enumerate(dates) if issametestDay(self.time_stamp, x) & issameTDMS(self.tdmsNumber, tdmsNumbers[i])]
            if inds:
                indRow = inds[0]
                self.procNumber = str(int(sheet.cell(indRow, 2).value))
                self.PXX = str(int(sheet.cell(indRow, 3).value))
                self.PYY = str(int(sheet.cell(indRow, 4).value))
                self.mmotecnum = format(int(sheet.cell(indRow, 5).value), '03d')           # YYY do FID
                self.FIDNumber = str(int(sheet.cell(indRow, 6).value))                     # Z do FID
                self.codefinalNumber = format(int(sheet.cell(indRow, 7).value), '03d')     # XXX do FID
            else:
                print('Make sure the test from ' + self.yyyymmmdd + ' ' + self.HHMMSS + ' is related with the campaign XL file!')
        else:
            print('Make sure ' + xlName + ' file has the correct header!')

    # Generate plot to be used on the report
    def gen_plots(self):
        # Read the TDMS data
        rack_1 = TdmsFile(self.file_1)
        rack_2 = TdmsFile(self.file_2)

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

        # Filtering data (Butterwoth band filter)
        fs = 1000
        lowcut = 10
        highcut = 300
        cutoff = 20
        order = 5
        # PT104_filt = but_filter(PT104, lowcut, highcut, fs, order)
        PT104_filt = butter_lowpass_filtfilt(PT104, cutoff, fs, order)
        plt.figure(1)
        plt.clf()
        plt.plot(Time, PT104, label = 'Noisy PT104 signal')
        plt.plot(Time, PT104_filt, label = 'Filtered PT104 signal (<{} Hz)'.format(str(cutoff)))
        plt.xlabel('Time [s]')
        plt.ylabel("Pressure [bar]")
        plt.grid(True)
        plt.axis('tight')
        plt.legend(loc = 'best')
        dirPath = osp.dirname(self.file_1)
        plt.savefig(osp.join(dirPath, 'PT104' + '_' + self.memoCode), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')


        # PT104_sosfilt = butter_lowpass_sosfiltfilt(PT104, cutoff, fs, order)
        # plt.figure(2)
        # plt.clf()
        # plt.plot(Time, PT104, label = 'Noisy PT104 signal')
        # plt.plot(Time, PT104_sosfilt, label = 'SOS Filtered PT104 signal (<{} Hz)'.format(str(cutoff)))
        # plt.xlabel('Time [s]')
        # plt.ylabel("Pressure [bar]")
        # plt.grid(True)
        # plt.axis('tight')
        # plt.legend(loc = 'best')
        # plt.show()
        # plt.savefig('PT104' + '_' + self.memoCode, dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')

        # Fixing offset
        # pass

        # ########################################################################################
        # # Plots
        # fig = plt.figure("Time plots after correction", figsize = (10, 6), dpi = 80)
        # plt.plot(Time_1, color = "blue", linewidth = 2, linestyle = "-", label = "rack_1 time")
        # plt.plot(Time_2, color = "red",  linewidth = 2, linestyle = "-", label = "rack_2 time")
        # plt.legend(loc = 'upper left')
        # plt.grid()
        # plt.title("Time from racks after Synchronization")
        # plt.xlabel("Index")
        # plt.ylabel("Time [s]")
        # plt.savefig('SyncTime' + '_' + self.memoCode, dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
        # # plt.show()

        # fig = plt.figure("Basic Plots", figsize = (10, 6), dpi = 80)
        # plt.plot(Time, PT103, color = "blue", linewidth = 2, linestyle = "-", label = "PT103")
        # plt.plot(Time, PT104, color = "red",  linewidth = 2, linestyle = "-", label = "PT104")
        # plt.legend(loc = 'center left')
        # plt.grid()
        # plt.title("Pressure transducer signals")
        # plt.xlabel("Time [s]")
        # plt.ylabel("Pressure [bar]")
        # plt.savefig('Prss' + '_' + self.memoCode, dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
        # # plt.show()

        # fig = plt.figure("Torquemeter", figsize = (10, 6), dpi = 80)
        # plt.plot(Time, MT401T, color = "blue", linewidth = 2, linestyle = "-", label = "MT401T")
        # plt.plot(Time, MT401J, color = "red",  linewidth = 2, linestyle = "-", label = "MT401J")
        # plt.legend(loc = 'lower center')
        # plt.grid()
        # plt.title("Pressure transducer signals")
        # plt.xlabel("Time [s]")
        # plt.ylabel("Torque [N.m] & Power [kW]")
        # plt.savefig('Trqm' + '_' + self.memoCode, dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
        # # plt.show()
        # ########################################################################################

# Check if the TDMS correpond to the same test using time stamp data
def checkTDMS_byts(path_to_file_1, path_to_file_2):
    # Read the TDMS data
    rack_1 = TdmsFile(path_to_file_1)
    rack_2 = TdmsFile(path_to_file_2)

    # Root objects 
    root_object_1 = rack_1.object()
    root_object_2 = rack_2.object()

    #time stamps
    time_stamp_1 = root_object_1.property("Created")
    time_stamp_2 = root_object_2.property("Created")

    if (time_stamp_1 - time_stamp_2).total_seconds() < 2:   # <2s delay between tdms criation, usually
        return True
    else:
        return False

def getMemotecFormatFilePath(TDMSfilepath):
	if osp.exists(osp.join(osp.dirname(TDMSfilepath), memoFormatName)):
		return osp.dirname(TDMSfilepath)
	elif osp.exists(osp.join(osp.dirname(osp.dirname(TDMSfilepath)), memoFormatName)):
		return osp.dirname(osp.dirname(TDMSfilepath))
	else:
		print('There is no ' + memoFormatName + '!')
		return

# Compare dates from TDMS time stamp and from excel date
def issametestDay(date1, date2_cell):
    if date2_cell.ctype == 3:                    # http://xlrd.readthedocs.io/en/latest/api.html#xlrd.sheet.Cell
        if (date1.replace(tzinfo = None) - xlrd.xldate.xldate_as_datetime(date2_cell.value, 0)).days == 0:
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
def add_testInfo(path_to_file_1, path_to_file_2):
    templateNames = [memoFormatName, memoDeParaData, logoName]

    # Initialize as a testInfo class instance
    test = testInfo(file_1 = path_to_file_1, file_2 = path_to_file_2)

    if checkTDMS_byts(test.file_1, test.file_2):            # Cross check is TDMS correspond to same test
        test.add_datetime_strs()                            # Add date/time information to test
        test.gen_plots()                                    # Generate plots
        test.add_tex_info(templateNames)                    # Add tex templates information
        test.add_xl_info(TestInfoxlName)                    # Add information from campaign XL file
        return test
    else:
        print("Make sure {} and {} are from the same test!".format(osp.basename(test.file_1), osp.basename(test.file_2)))
        return ()

def butter_lowpass_filtfilt(data, cutoff, fs, order = 5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype = 'low', analog = False)
    data_filt = filtfilt(b, a, data)
    return data_filt

def butter_lowpass_sosfiltfilt(data, cutoff, fs, order = 5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    sos = butter(order, normal_cutoff, btype = 'low', analog = False, output = 'sos')
    data_filt = sosfiltfilt(sos, data)
    return data_filt

# Test case
if __name__ == '__main__':
    # Path to file
    path_to_file_1 = '/Users/roncha/pyDev/auto_rep/COMPLETO_10_31_43_AM_16_08_16_P04.tdms'
    path_to_file_2 = '/Users/roncha/pyDev/auto_rep/LOx_pump_Rack2_10_31_44_AM_16_08_16_P04.tdms'
    add_testInfo(path_to_file_1, path_to_file_2)
