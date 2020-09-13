# Standard imports
import os
import re
import time as tm
from datetime import datetime, timedelta, timezone
from bisect import bisect_left
from shutil import copy

# PyPI imports
import scipy.io as sio
from nptdms import TdmsFile
import numpy as np

# Local imports
from tools import transform_data

# Globals
delimiter = '_'


class TestCamp:
    __TC_counter = 0  # Test Campaign universal counter

    def __init__(self, name, specimen, bench, client, DAQ_list, TD_list=None):
        self.name = name
        self.specimen = specimen
        self.test_bench = bench
        self.client = client
        self.DAQ_list = DAQ_list
        self.TD_lst = []
        if TD_list is not None:
            for td in TD_list:
                self.add_TD(td)
        TestCamp.__TC_counter += 1

    def __repr__(self):
        return 'TestCamp(\'' + self.name + '\', \'' + self.specimen + '\', \'' + self.test_bench + '\', \'' + \
               self.client + '\')'

    def __str__(self):
        return 'The test campaign {} occurred at {} test bench as a {}\'s request to analyze the performance of the ' \
               '{}.'.format(self.name, self.test_bench, self.client, self.specimen)

    # def print_DAQs(self):
    #     print('The test campaign {} has {} DAQ\'s:'.format(self.name, len(self.DAQ_list)))
    #     for daq in self.DAQ_list:
    #         print(daq)

    # def print_TDs(self):
    #     print('The test campaign {} has {} Test Day(s):'.format(self.name, len(self.TD_lst)))
    #     for td in self.TD_lst:
    #         print(td)

    def fullname(self):
        """
        Standard test campaign fullname generator.
        """
        fullname = self.name
        if not self.name == self.specimen:
            fullname += delimiter + self.specimen

        fullname += delimiter + self.test_bench

        if self.TD_lst:
            if self.TD_lst[0].date == self.TD_lst[-1].date:
                fullname += delimiter + str(self.TD_lst[0].year)
            else:
                fullname += delimiter + str(self.TD_lst[0].year) + '-' + str(self.TD_lst[-1].year)
        return fullname

    def add_TD(self, TD):
        """
        Add (in a sorted way) a TestDay to TestCamp.TD_lst.
        """
        if isinstance(TD, TestDay):
            if TD not in self.TD_lst:
                ind = bisect_left([td.date for td in self.TD_lst], TD.date)
                self.TD_lst.insert(ind, TD)
                self.update_TD_rel_counter()
                self.update_Run_counters()
        else:
            return 0

    def rmv_TD(self, TD):
        """
        Remove (in a sorted way) a TestDay from the TestCamp.TD_lst.
        """
        if isinstance(TD, TestDay):
            if TD in self.TD_lst:
                self.TD_lst.pop(self.TD_lst.index(TD))
                self.update_TD_rel_counter()
                self.update_Run_counters()
        else:
            return 0

    def update_TD_rel_counter(self):
        """
        Update TD_lst relative counter.
        """
        for ind, td in enumerate(self.TD_lst):
            td.set_rel_counter(ind)

    def update_Run_counters(self):
        """
        Update Run.abs_counter and Run.rel_counter of Runs from TD's of the campaign.
        """
        counter = 0
        for td in self.TD_lst:
            td.update_Run_rel_counter()
            for run in td.Run_lst:
                counter += 1
                run.set_abs_counter(counter)

    def allocate_data_2_fldr_strt(self, root_folder):
        """
        Distribute all data files from test campaign in a standard folder structure in the root_folder.
        """
        self.update_TD_rel_counter()
        self.update_Run_counters()
        TC_folder = os.path.join(root_folder, self.fullname())
        if not os.path.exists(TC_folder):
            os.makedirs(TC_folder)
        for td in self.TD_lst:
            TD_folder = os.path.join(TC_folder, td.fullname())
            if not os.path.exists(TD_folder):
                os.makedirs(TD_folder)
            for run in td.Run_lst:
                Run_folder = os.path.join(TD_folder, run.fullname())
                if not os.path.exists(Run_folder):
                    os.makedirs(Run_folder)
                for file in Run.f_lst:
                    copy(file, Run_folder)
        self.print_fldr_strt(root_folder)

    def find_ts(self, file):
        """
        Return the correct time stamp of a file, based on filename generator characteristics of the Test Campaign's DAQs.
        """
        file_name = os.path.basename(file)
        daq = self.which_DAQ(self.DAQ_list, file)
        if daq.name == daqName1 or daq.name == daqName2:
            file_name = file_name.replace(daq.pref, '').replace(daq.suff, '').split(delimiter)
            file_name = file_name[0] + file_name[2] + file_name[3] + file_name[4]
            file_name = daq.pref + file_name + daq.suff
        ts = self.extract_ts_filename(file_name, daq.pref, daq.suff, daq.ts_fmt)
        ts = ts - daq.ts_off
        return ts

    @classmethod
    def from_file_list(cls, file_list):
        """
        Class constructor from a file list.
        """
        for file in file_list:
            pass

    @staticmethod
    def extract_ts_filename(file_name, prefix, suffix, time_stamp_format):
        """
        Extract time stamp from filename besed on prefix + time stamp + suffix structure.
        """
        return datetime.strptime(file_name.replace(prefix + delimiter, '').replace(delimiter + suffix, ''),
                                 time_stamp_format)

    @staticmethod
    def which_DAQ(DAQ_list, file):
        """
        Return the DAQ (from DAQ_list) the data file was acquired from.
        """

        if not all([isinstance(daq, DAQ) for daq in DAQ_list]):
            return 0

        bol_lst = [daq.isFilefromDAQ(file) for daq in DAQ_list]

        if bol_lst.count(True) == 1:
            return DAQ_list[bol_lst.index(True)]
        else:
            return 0

    @staticmethod
    def print_fldr_strt(folder):
        """
        Print the folder (directory) tree.
        """
        for (root, dirs, files) in os.walk(folder, topdown=True):
            print(root)
            print(dirs)
            print(files)
            print('-------------------------------------------')

    @staticmethod
    def gen_Run_rprt(run, DAQ_list, template):
        """
        Generate report from a specific Run using template.
        """

        if run.isfull_Run(DAQ_list):
            run = run.split_f_list_in_DAQ(DAQ_list)
            # gen_Run_plots(run, template)
        else:
            return 0


class DAQ:
    def __init__(self, name, sample_rate, file_amount, prefix, suffix, time_stamp_format, time_stamp_offset=None):
        self.name = name
        self.rate = sample_rate
        self.f_amt = file_amount
        self.prefix = prefix
        self.suffix = suffix
        self.ts_fmt = time_stamp_format

        self.ts_off = timedelta(seconds=0)
        if not time_stamp_offset is None:
            self.ts_off = time_stamp_offset

    def __repr__(self):
        return 'DAQ(\'' + self.name + '\', ' + str(self.rate) + ')'

    def __str__(self):
        return '{} --- {} Hz --- [{}] {}_XXX_{}'.format(self.name, self.rate, self.f_amt, self.prefix, self.suffix)

    def isFilefromDAQ(self, file):
        name = os.path.basename(file)
        if name.startswith(self.prefix) and name.endswith(self.suffix):
            return True
        else:
            return False

    # Factory of DAQ's
    @classmethod
    def PXI_LF(cls):
        return cls('PXI_LF', 1000, 1, 'Turbine_IAE', '.tdms', '%Y_%m_%d_%H_%M_%S')

    @classmethod
    def PXI_LF_01(cls):
        daq = DAQ.PXI_LF()
        daq.name += delimiter + '01'
        daq.prefix += delimiter + 'Rack' + '01'
        return daq

    @classmethod
    def PXI_LF_02(cls):
        daq = DAQ.PXI_LF()
        daq.name += delimiter + '02'
        daq.prefix += delimiter + 'Rack' + '02'
        return daq

    @classmethod
    def PXI_HF(cls):
        return cls('PXI_HF', 10000, 1, 'R02S06_PXIe-4499', '.tdms', '%d-%m-%Y_%H-%M-%S')

    @classmethod
    def HBM(cls):
        return cls('HBM', 1200, 1, HBMpref, '1200Hz.MAT', '%Y_%m_%d_%H_%M_%S')

    # @classmethod
    # def DAQX_LF(cls):
    #     return cls(daqName1, daqSR1, daqNfile1, daqPref1, daqSuff1, '%y%m%d%H%M%S', timedelta(minutes=51, seconds=10))
    #
    # @classmethod
    # def DAQX_HF(cls):
    #     return cls(daqName2, daqSR2, daqNfile2, daqPref1, daqSuff2, '%y%m%d%H%M%S', timedelta(minutes=51, seconds=10))


class TestDay:
    def __init__(self, date, logbook, Run_list=None):
        self.date = date
        self.name = self.date.strftime('%Y-%m-%d')
        self.logbook = logbook
        self.Run_lst = []
        if Run_list is not None:
            for run in Run_list:
                if run.t_stmp.date() == self.date:
                    self.add_Run(run)
        self.rel_counter = 0

    def __repr__(self):
        return 'TestDay(' + repr(self.date) + ')'

    def __str__(self):
        return 'Test Day {} --- {} Run(s)'.format(self.name, len(self.Run_lst))

    def fullname(self):
        return 'TestDay' + str(self.rel_counter).zfill(2) + delimiter + self.name

    def print_Runs(self):
        print(repr(self) + ':')
        for run in self.Run_lst:
            print(run)

    def add_Run(self, RUN):
        """
        Add (in a sorted way) a Run to TestDay.Run_lst.
        """
        if isinstance(RUN, Run):
            if RUN not in self.Run_lst:
                ind = bisect_left([run.t_stmp for run in self.Run_lst], RUN.t_stmp)
                self.Run_lst.insert(ind, RUN)
                self.update_Run_rel_counter()
        else:
            return 0

    def rmv_Run(self, RUN):
        """
        Remove (in a sorted way) a Run from TestDay.Run_lst.
        """
        if not isinstance(RUN, Run):
            if RUN in self.Run_lst:
                self.Run_lst.pop(self.Run_lst.index(RUN))
                self.update_Run_rel_counter()
        else:
            return 0

    def update_Run_rel_counter(self):
        """
        Update Run_lst relative counter.
        """
        for ind, run in enumerate(self.Run_lst):
            run.set_rel_counter(ind)

    def set_rel_counter(self, counter):
        self.rel_counter = counter


class Run:
    def __init__(self, time_stamp, file_list=None):
        self.t_stmp = time_stamp
        self.name = self.t_stmp.strftime('%Y-%m-%d-%H-%M-%S')

        self.f_lst = []
        if not file_list is None:
            for file in file_list:
                self.add_file(file)

        self.rel_counter = 0
        self.abs_counter = 0

    def __repr__(self):
        return 'Run(' + repr(self.t_stmp) + ')'

    def __str__(self):
        return 'Run {} has {} file(s)'.format(self.name, len(self.f_lst))

    def fullname(self):
        return 'Run' + str(self.rel_counter).zfill(2) + delimiter + 'absRun' + str(self.abs_counter).zfill(3) + \
               delimiter + self.name

    def print_files(self):
        print(str(self) + ':')
        for file in self.f_lst:
            print(file)

    def add_file(self, file):
        self.f_lst.append(file)

    def split_f_list_in_DAQ(self, DAQ_list):
        """
        Distribute files into a list of file lists correlated (same index) to each DAQ from DAQ list.
        """
        if all([isinstance(daq, DAQ) for daq in DAQ_list]):
            f_lst_DAQ = [[] for daq in DAQ_list]
            for file in self.f_lst:
                bol_lst = [daq.isFilefromDAQ(file) for daq in DAQ_list]
                if bol_lst.count(True) == 1:
                    ind = bol_lst.index(True)
                    f_lst_DAQ[ind].append(file)
                else:
                    print('{} was not generated by any DAQ.'.format(file))
            return f_lst_DAQ
        else:
            return 0

    def isfull_Run(self, DAQ_list):
        """
        Check if Run has all files generated by DAQ's from DAQ_list.
        """
        rqst_amnt = [daq.f_amt for daq in DAQ_list]
        f_lst_DAQ = self.split_f_list_in_DAQ(DAQ_list)
        avlb_amnt = [len(lst) for lst in f_lst_DAQ]
        if rqst_amnt == avlb_amnt:
            return True
        else:
            return False

    def set_rel_counter(self, counter):
        self.rel_counter = counter

    def set_abs_counter(self, counter):
        self.abs_counter = counter


class Template:
    def __init__(self, TexTemplate, file_list=None):
        self.tex_temp = TexTemplate
        pass


class DataFile:
    """
    Any file generated by a data acquisition system. It has a list of DataChannel objects.
    """
    def __init__(self, file):
        self.file = file
        self.name = self.file.name
        self.format = self.name.split('.')[-1]
        self.channels = []
        self.extract_all_channels()

    def add_channel(self, channel):
        if isinstance(channel, DataChannel):
            self.channels.append(channel)
        else:
            print(channel, 'is not a DataChannel object.')

    def rmv_channel(self, channel):
        if isinstance(channel, DataChannel):
            self.channels.remove(channel)
        else:
            print(channel, 'is not a DataChannel object.')

    def find_all_channel_tags(self):
        all_tags = []
        if self.format is 'tdms':
            for channel in TdmsFile.read(self.file).groups()[0].channels():
                all_tags.append(channel.name)
        elif self.format is 'MAT':
            data = sio.loadmat(self.file, squeeze_me=True)
            for key in data.keys():
                if 'Channel' in key and 'Header' in key:
                    all_tags.append(data[key].tolist()[-1])
        elif self.format is 'mat':
            all_tags = sio.loadmat(self.file, squeeze_me=True).keys()
        elif self.format is 'txt':
            with open(self.file, 'r') as txt:
                for line in txt:
                    if 'x' in line and 'y' in line:
                        cols = line.split()
                        for i, col in enumerate(cols):
                            all_tags[i] = col.split('[')[0].replace('y,', '')
        else:
            print(self.format, 'not implemented.')
        return all_tags

    def find_all_channel_units(self):
        all_units = []
        if self.format is 'tdms':
            for channel in TdmsFile.read(self.file).groups()[0].channels():
                all_units.append(channel.properties['Unit'])
        elif self.format is 'MAT':
            data = sio.loadmat(self.file, squeeze_me=True)
            for key in data.keys():
                if 'Channel' in key and 'Header' in key:
                    all_units.append(data[key].tolist()[1])
        elif self.format is 'mat':
            all_tags = self.find_all_channel_tags()
            for tag in all_tags:
                if tag.endswith('_X'):
                    unit = 's'
                else:
                    if tag.startswith('P'):
                        unit = 'Pa'
                    elif tag.startswith('V'):
                        unit = 'm/s^2'
                    elif tag.startswith('SYNC'):
                        unit = 'V'
                    else:
                        unit = None
                        print(tag, 'does not have unit implemented.')
                all_units.append(unit)
        elif self.format is 'txt':
            with open(self.file, 'r') as txt:
                for line in txt:
                    if 'x' in line and 'y' in line:
                        cols = line.split()
                        for i, col in enumerate(cols):
                            all_units[i] = col.split('[')[1].split(']')[0]
        return all_units

    def extract_all_channels(self):
        all_data = []
        all_tags = self.find_all_channel_tags()
        all_units = self.find_all_channel_units()
        if self.format is 'tdms':
            raw_data = TdmsFile.read(self.file).groups()[0]
            for tag in all_tags:
                all_data.append(raw_data[tag][:])
            if raw_data[tag].is_waveform():  # It uses last tag (from previous for loop) for simplicity
                all_tags.append('time')
                all_units.append('s')
                all_data.append(raw_data[tag].time_track())
                all_tags.append('time_abs')
                all_units.append('s')
                all_data.append(raw_data[tag].time_track(absolute_time=True, accuracy='us'))
        elif self.format is 'MAT':
            raw_data = sio.loadmat(self.file, squeeze_me=True)
            for key in raw_data.keys():
                if 'Channel' in key and 'Data' in key:
                    all_data.append(raw_data[key])
        elif self.format is 'mat':
            raw_data = sio.loadmat(self.file, squeeze_me=True)
            for tag in all_tags:
                all_data.append(raw_data[tag])
        elif self.format is 'txt':
            with open(self.file, 'r') as txt:
                for line in txt:
                    if 'ch' not in line and line != '\n':
                        for i in range(len(all_tags)):
                            all_data[i].append(line.split()[i])
        for tag, unit, data in zip(all_tags, all_units, all_data):
            self.add_channel(DataChannel(tag, unit, np.array(list(map(float, data)))))
        return print('All data extracted from', self.name)

    def find_time_channels(self):
        time_channels = []
        time_abs_channels = []
        time_tags = ['time', 'x']
        time_units = ['s']
        time_abs_tags = ['abs']
        for channel in self.channels:
            for tag in time_tags:
                match_tag = re.search(tag, channel.tag, flags=re.IGNORECASE)
                if match_tag:
                    for unit in time_units:
                        match_unit = re.search(unit, channel.unit, flags=re.IGNORECASE)
                        if match_unit:
                            time_channels.append(channel)
        for channel in time_channels:
            for tag in time_abs_tags:
                match_absolute = re.search(tag, channel.tag, flags=re.IGNORECASE)
                if match_absolute:
                    for i, timestamp in enumerate(channel.data):
                        dt_raw = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        platform_epoch = datetime.fromtimestamp(tm.mktime(tm.localtime(0)), tz=timezone.utc)
                        ni_epoch = datetime(1904, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
                        channel.data[i] = dt_raw - (platform_epoch - ni_epoch)
                    time_abs_channels.append(channel)
        if len(time_channels) > 1 or len(time_abs_channels) > 1:
            return print('There are too many time references on file:', self.name)
        elif len(time_channels) == 0 and len(time_abs_channels) == 0:
            return print('There is no time channels on file:', self.name)
        else:
            return time_channels, time_abs_channels

    def set_time_references(self, time_abs_event):
        time_channels, time_abs_channels = self.find_time_channels()
        if len(time_abs_channels) == 1:
            tag = time_abs_channels[0].tag.replace('_abs', '')
            unit = 's'
            data = transform_data.abs2rel(time_abs_channels[0].data)
            if len(time_channels) == 1:
                self.rmv_channel(time_channels[0])
        else:
            time_offset = 0
            tag = time_abs_channels[0].tag.replace('time_', 'time_abs_')
            unit = 's'
            data = transform_data.create_time_abs(time_channels[0].data, time_abs_event, time_offset)
        self.add_channel(DataChannel(tag, unit, data))


class DataChannel:
    """
    Smallest unit of test data.
    """
    def __init__(self, tag, unit, data_array):
        self.tag = tag
        self.unit = unit
        self.data = data_array

    @staticmethod
    def is_waveform(channel):
        try:
            channel.time_track()
            return True
        except KeyError:  # KeyError if channel doesn't have waveform data (info from npTDMS package)
            return False
