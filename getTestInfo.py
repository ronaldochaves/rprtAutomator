# headers
import numpy as np
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from datetime import datetime, date
import os.path as osp
import xlrd
from scipy.signal import butter, filtfilt, sosfiltfilt
import scipy.io as sio


# Globals
tex_template_repo = 'template_repo'
TexTemplateName = 'memoFill.tex'
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
        self.ddmmyyyy = time_stamp.strftime("%d-%m-%Y")
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
        # template_repo_path = getTemplateRepoPath(self.file_1)
        template_repo_path = '/Users/roncha/pyDev/auto_rep/template_repo'
        self.template_repo_path = template_repo_path
        self.TexTemplatePath = osp.join(template_repo_path, TexTemplateName)
        template_repo_path = template_repo_path.replace('\\', '/')                  # LaTeX demands '/' as folder separation, even on Windows
        self.template_repo = template_repo_path
        # self.memoFormatFileUm = osp.join(self.template_repo, memoFormat)
        # self.memoFormatFileDois = osp.join(self.template_repo, memoDeParaData)
        # self.IAElogoPath = osp.join(self.template_repo, logo)
        path_split = self.file_1.rsplit('.', 1)
        self.tdmsNumber = (path_split[0])[-3:-1]                # Point ID on the TDMS file name (it can be improved!)
        self.disclaimer = ('Generated automatically in ' + datetime.now().strftime('%d %b %Y') 
            + '; manual alteration of this file is STRONGLY discouraged!')
        # self.foldPath = osp.dirname(self.file_1)

    # Add basic information from XL campaign file
    def add_xl_info(self, xlName):
        xlsx = xlrd.open_workbook(osp.join(self.template_repo_path, xlName))
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

    # Generate plots to be used on the report
    def gen_plots(self):
        # Read .mat data
        data_hbm = sio.loadmat(self.file_1)

        # Read .TDMS data
        rack_1 = TdmsFile(self.file_2)
        rack_2 = TdmsFile(self.file_3)
        rack_hv = TdmsFile(self.file_4)

        # Get groups (rack names)                 # automatize in the future
        group_names_1 = rack_1.groups()
        group_names_2 = rack_2.groups()
        group_names_hv = rack_hv.groups()

        # Synchronize relative times from racks

        # Time_1 = rack_1.channel_data(group_names_1[0], "System Time")
        # Time_2 = rack_2.channel_data(group_names_2[0], "System Time")
        # Time_hv = [0:9:0.0001]
        # indminLOx, indmaxLOx, indminTPU, indmaxTPU = syncTime(Time_1, Time_2)
        # Time = Time_1[indminTPU:indmaxTPU]

        indmin_hbm = 2*1200
        indmin_1 = 1*1000
        indmin_2 = 500
        indmin_hv = 0
        indmax_hbm = indmin_hbm + 9*1200
        indmax_1 = indmin_1 + 9*1000
        indmax_2 = indmin_2 + 9*1000
        indmax_hv = indmin_hv + 9*10000

        Time_hbm = np.linspace(0, 9, 10800)
        Time_1 = np.linspace(0, 9, 9000)
        Time_2 = np.linspace(0, 9, 9000)
        Time_hv = np.linspace(0, 9, 90000)

        # Get the (really useful) data from channels
        var = data_hbm['Channel_31_Data'][ndmin_hbm:indmax_hbm]
        PT101 = (rack_1.channel_data(group_names_1[0], "PT101"))[indmin_1:indmax_1]
        PT102 = (rack_1.channel_data(group_names_1[0], "PT102"))[indmin_1:indmax_1]
        PT103 = (rack_2.channel_data(group_names_2[0], "PT103"))[indmin_2:indmax_2]
        PT104 = (rack_2.channel_data(group_names_2[0], "PT104"))[indmin_2:indmax_2]
        PT551 = (rack_1.channel_data(group_names_1[0], "PT551"))[indmin_1:indmax_1]
        PT552 = (rack_1.channel_data(group_names_1[0], "PT552"))[indmin_1:indmax_1]
        PT553 = (rack_1.channel_data(group_names_1[0], "PT553"))[indmin_1:indmax_1]
        PT421 = (rack_1.channel_data(group_names_1[0], "PT421"))[indmin_1:indmax_1]
        MT401S = (rack_1.channel_data(group_names_1[0], "MT401S"))[indmin_1:indmax_1]
        MT401T = (rack_1.channel_data(group_names_1[0], "MT401T"))[indmin_1:indmax_1]
        MT401J = (rack_1.channel_data(group_names_1[0], "MT401J"))[indmin_1:indmax_1]
        MV101F = (rack_1.channel_data(group_names_1[0], "MV101F"))[indmin_1:indmax_1]
        TTCEMEDIA = (rack_1.channel_data(group_names_1[0], "TTCEMEDIA"))[indmin_1:indmax_1]
        ai4 = (rack_hv.channel_data(group_names_hv[0], 'ai4'))[indmin_hv:indmax_hv]

        # Filtering data (Butterwoth band filter)
        fs = 1000
        lowcut = 10
        highcut = 300
        cutoff = 20
        order = 5
        # PT104_filt = but_filter(PT104, lowcut, highcut, fs, order)
        PT104_filt = butter_lowpass_filtfilt(PT104, cutoff, fs, order)
        fig = plt.figure("PT104 with Butterwoth Filter", figsize = (10, 6), dpi = 80)
        plt.plot(Time_1, PT104, label = 'Noisy PT104 signal')
        plt.plot(Time_1, PT104_filt, label = 'Filtered PT104 signal (<{} Hz)'.format(str(cutoff)))
        plt.xlabel('Time [s]')
        plt.ylabel("Pressure [bar]")
        plt.grid()
        plt.axis('tight')
        plt.legend(loc = 'best')
        dirPath = osp.dirname(self.file_2)
        # plt.savefig(osp.join(dirPath, 'PT104' + '_' + self.memoCode), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
        plt.savefig(osp.join(dirPath, 'PT104' + '_' + self.memoCode + '.pdf'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait')

        ai4_filt = butter_lowpass_filtfilt(ai4, cutoff, fs, order)
        # ai4_rms = np.sqrt(np.mean(ai4_filt**2))
        # print(ai_rms)
        fig = plt.figure("ai4 with Butterwoth Filter", figsize = (10, 6), dpi = 80)
        plt.plot(Time_hv, ai4, label = 'Noisy ai4 signal')
        plt.plot(Time_hv, ai4_filt, label = 'Filtered ai4 signal (<{} Hz)'.format(str(cutoff)))
        plt.xlabel('Time [s]')
        plt.ylabel("Pressure [bar]")
        plt.grid()
        plt.axis('tight')
        plt.legend(loc = 'best')
        dirPath = osp.dirname(self.file_4)
        # plt.savefig(osp.join(dirPath, 'PT104' + '_' + self.memoCode), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait', format = 'eps')
        plt.savefig(osp.join(dirPath, 'ai4' + '_' + self.memoCode + '.pdf'), dpi = 80, facecolor = 'w', edgecolor = 'w', orientation = 'portrait')

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
def checkTDMS_byts(path_to_file_1, path_to_file_2, path_to_file_3, path_to_file_4):
    # Read .mat data
    data_hbm = sio.loadmat(path_to_file_1)

    # Read the TDMS data
    rack_1 = TdmsFile(path_to_file_2)
    rack_2 = TdmsFile(path_to_file_3)
    rack_hv = TdmsFile(path_to_file_4)

    # Root objects 
    root_object_1 = rack_1.object()
    root_object_2 = rack_2.object()
    root_object_hv = rack_hv.object()

    # Time stamps
    time_stamp_hbm = datetime.strptime(data_hbm['File_Header']['Date'][0, 0], '%d/%m/%Y %H:%M:%S')
    time_stamp_1 = root_object_1.property("Created")
    time_stamp_2 = root_object_2.property("Created")
    time_stamp_hv = root_object_hv.property("Created")

    if (time_stamp_1 - time_stamp_2).total_seconds() < 2 && (time_stamp_1 - time_stamp_hv).total_seconds() < 2 && (time_stamp_2 - time_stamp_hv).total_seconds() < 2:   # <2s delay between tdms criation, usually
        return True
    else:
        return False

def getTemplateRepoPath(TDMSfilepath):
    # memoFormatpath = osp.join(tex_template_repo, memoFormatName)
    template_rel_path = osp.join(tex_template_repo, TexTemplateName)
    if osp.exists(osp.join(osp.dirname(TDMSfilepath), template_rel_path)):
        return osp.join(osp.dirname(TDMSfilepath), tex_template_repo)
    elif osp.exists(osp.join(osp.dirname(osp.dirname(TDMSfilepath)), template_rel_path)):
        return osp.join(osp.dirname(osp.dirname(TDMSfilepath)), tex_template_repo)
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
def add_testInfo(path_to_file_1, path_to_file_2, path_to_file_3, path_to_file_4):
    templateNames = [memoFormatName, memoDeParaData, logoName]

    # Initialize as a testInfo class instance
    test = testInfo(file_1 = path_to_file_1, file_2 = path_to_file_2, file_3 = path_to_file_3, file_4 = path_to_file_4)

    if checkTDMS_byts(test.file_1, test.file_2, test.file_3, test.file_4):       # Cross check is TDMS correspond to same test
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
    file_hbm = '/Users/roncha/pyDev/auto_rep/Terte3/Fuel Pump Test - HBM/08-11-2018/P23_2018_11_08_13_01_51_1200Hz.mat'
    file_pxi_1 = '/Users/roncha/pyDev/auto_rep/Terte3/Fuel Pump Test - PXI/08-11-2018/Turbine_Rack01_2018_11_08_13_01_51.tdms'
    file_pxi_2 = '/Users/roncha/pyDev/auto_rep/Terte3/Fuel Pump Test - PXI/08-11-2018/Turbine_Rack02_2018_11_08_13_01_51.tdms'
    file_pxi_hv = '/Users/roncha/pyDev/auto_rep/Terte3/Fuel Pump Test - PXI/08-11-2018/R02S06_PXIe-4499_08-11-2018_13-01-52.tdms'

    add_testInfo(file_hbm, file_pxi_1, file_pxi_2, file_pxi_hv)
