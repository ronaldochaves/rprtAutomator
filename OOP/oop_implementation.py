# Standard imports
import os
import re
import time as tm
from datetime import date, datetime, timedelta, timezone
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
        Return the correct time stamp of a file, based on filename generator characteristics of the Test Campaign's
        DAQs.
        """
        file_name = os.path.basename(file)
        daq = self.which_DAQ(self.DAQ_list, file)
        # if daq.name == daqName1 or daq.name == daqName2:
        #     file_name = file_name.replace(daq.pref, '').replace(daq.suff, '').split(delimiter)
        #     file_name = file_name[0] + file_name[2] + file_name[3] + file_name[4]
        #     file_name = daq.pref + file_name + daq.suff
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

        bol_lst = [daq.has_file(file) for daq in DAQ_list]

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
    def __init__(self, name, prefixes, suffixes, time_stamp_formats, time_stamp_offset=None):
        self.name = name

        self.naming_style = []
        if len(prefixes) == len(suffixes) and len(prefixes) == len(time_stamp_formats):
            self.files_amount = len(prefixes)
            for prefix, suffix, ts_format in zip(prefixes, suffixes, time_stamp_formats):
                self.naming_style.append(NamingStyle(prefix, suffix, ts_format))
        else:
            print('Naming style not satisfied.')

        self.ts_off = timedelta(seconds=0)
        if not time_stamp_offset is None:
            self.ts_off = time_stamp_offset

    def __str__(self):
        return '{} --- [{}] files'.format(self.name, self.files_amount)

    def has_file(self, file):
        if isinstance(file, DataFile):
            for style in self.naming_style:
                if style.has_naming_style(file):
                    return True
        else:
            print(file, 'not DataFile object.')
        return False

    # Factory of DAQ's
    @classmethod
    def PXI_LF(cls):
        return cls('PXI_LF', 'Turbine_IAE', '.tdms', '%Y_%m_%d_%H_%M_%S')

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
        # daq.prefix += delimiter + 'Rack' + '02'
        return daq

    @classmethod
    def PXI_HF(cls):
        return cls('PXI_HF', 'R02S06_PXIe-4499', '.tdms', '%d-%m-%Y_%H-%M-%S')

    # @classmethod
    # def HBM(cls):
    #     return cls('HBM', HBMpref, '1200Hz.MAT', '%Y_%m_%d_%H_%M_%S')

    # @classmethod
    # def DAQX_LF(cls):
    #     return cls(daqName1, daqPref1, daqSuff1, '%y%m%d%H%M%S', timedelta(minutes=51, seconds=10))
    #
    # @classmethod
    # def DAQX_HF(cls):
    #     return cls(daqName2, daqPref1, daqSuff2, '%y%m%d%H%M%S', timedelta(minutes=51, seconds=10))


class TestDay(date):
    def __init__(self, date, logbook, Run_list=None):
        self.date = date
        self.logbook = logbook
        self.Run_lst = []
        if Run_list is not None:
            for run in Run_list:
                if run.time_stamp.date() == self.date:
                    self.add_Run(run)
        self.rel_counter = 0

    def __repr__(self):
        return 'TestDay(' + repr(self.date) + ')'

    def __str__(self):
        return 'Test Day {} --- {} Run(s)'.format(self.date, len(self.Run_lst))

    def fullname(self):
        return 'TestDay' + str(self.rel_counter).zfill(2) + delimiter + self.date

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
                ind = bisect_left([run.time_stamp for run in self.Run_lst], RUN.time_stamp)
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
        self.time_stamp = time_stamp
        self.name = self.time_stamp.strftime('%Y-%m-%d-%H-%M-%S')

        self.f_lst = []
        if not file_list is None:
            for file in file_list:
                self.add_file(file)

        self.rel_counter = 0
        self.abs_counter = 0

    def __repr__(self):
        return 'Run(' + repr(self.time_stamp) + ')'

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
                bol_lst = [daq.has_file(file) for daq in DAQ_list]
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
        rqst_amnt = [daq.files_amount for daq in DAQ_list]
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

    @classmethod
    def time_channel(cls, reference, data_array):
        if reference == 'relative':
            return cls('time', 's', data_array)
        elif reference == 'absolute':
            return cls('time_abs', 's', data_array)


class NamingStyle:
    """
    Set of prefix, time stamp format and suffix for naming files.
    """

    def __init__(self, prefix, suffix, time_stamp_format):
        self.prefix = prefix
        self.suffix = suffix
        self.ts_format = time_stamp_format

    def has_naming_style(self, file):
        if isinstance(file, DataFile):
            if file.name.startswith(self.prefix) and file.format is self.suffix:
                return True
            else:
                print(file, 'does not have the name style:', self)
        else:
            print(file, 'is not a DataFile object.')
        return False

    def find_time_stamp(self, file):
        if self.has_naming_style(file):
            raw_time_stamp = file.name.replace(self.prefix, '').replace(self.suffix, '').replace('-', '_')
            ts_items = raw_time_stamp.split('_')
            for item in ts_items:
                if len(item) != 2 or len(item) != 4:
                    ts_items.remove(item)
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

    def remove_channel(self, channel):
        if isinstance(channel, DataChannel):
            self.channels.remove(channel)
        else:
            print(channel, 'is not a DataChannel object.')

    def replace_channel(self, channel_added, channel_removed):
        for i, channel in enumerate(self.channels):
            if channel == channel_removed:
                self.channels.pop(i)
                self.channels.insert(i, channel_added)

    def find_all_channel_tags(self):
        all_tags = []
        if self.format == 'tdms':
            for channel in TdmsFile.read(self.file).groups()[0].channels():
                all_tags.append(channel.name)
        elif self.format == 'MAT':
            data = sio.loadmat(self.file, squeeze_me=True)
            for key in data.keys():
                if 'Channel' in key and 'Header' in key:
                    all_tags.append(data[key].tolist()[-1])
        elif self.format == 'mat':
            all_tags = sio.loadmat(self.file, squeeze_me=True).keys()
        elif self.format == 'txt':
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
        if self.format == 'tdms':
            for channel in TdmsFile.read(self.file).groups()[0].channels():
                all_units.append(channel.properties['Unit'])
        elif self.format == 'MAT':
            data = sio.loadmat(self.file, squeeze_me=True)
            for key in data.keys():
                if 'Channel' in key and 'Header' in key:
                    all_units.append(data[key].tolist()[1])
        elif self.format == 'mat':
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
        elif self.format == 'txt':
            with open(self.file, 'r') as txt:
                for line in txt:
                    if 'x' in line and 'y' in line:
                        cols = line.split()
                        for i, col in enumerate(cols):
                            all_units[i] = col.split('[')[1].split(']')[0]
        return all_units

    def extract_all_channels(self):
        all_tags = self.find_all_channel_tags()
        all_units = self.find_all_channel_units()
        if self.format == 'tdms':
            raw_data = TdmsFile.read(self.file).groups()[0]
            for tag, unit in zip(all_tags, all_units):
                self.add_channel(DataChannel(tag, unit, raw_data[tag][:]))
            if raw_data.channels()[0].is_waveform():
                self.add_channel(DataChannel.time_channel('relative', raw_data.channels()[0].time_track()))
                self.add_channel(DataChannel.time_channel('absolute', raw_data.channels()[0].time_track(
                    absolute_time=True, accuracy='us')))
        elif self.format in ['mat', 'MAT']:
            raw_data = sio.loadmat(self.file, squeeze_me=True)
            for key, tag, unit in zip(raw_data.keys(), all_tags, all_units):
                if 'Channel' in key and 'Data' in key:
                    self.add_channel(DataChannel(tag, unit, raw_data[key]))
        elif self.format == 'txt':
            raw_data = []
            with open(self.file, 'r') as txt:
                for line in txt:
                    if 'ch' not in line and line != '\n':
                        for i in range(len(all_tags)):
                            raw_data[i].append(line.split()[i])
            for tag, unit, data in zip(all_tags, all_units, raw_data):
                self.add_channel(DataChannel(tag, unit, np.array(list(map(float, data)))))

        for channel in self.channels:
            if channel.tag in ['System Time', 'Time__1_-_default_sample_rate', 'x',] or channel.tag.endswith('_X'):
                self.replace_channel(channel, DataChannel.time_channel('relative', channel.data))
            elif channel.tag == 'Absolute Time':
                self.replace_channel(channel, DataChannel.time_channel('absolute', channel.data))
        return print('All data extracted from', self.name)

    @staticmethod
    def adjust_absolute_time(data):
        adjusted_data = []
        for i, timestamp in enumerate(data):
            dt_raw = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            platform_epoch = datetime.fromtimestamp(tm.mktime(tm.localtime(0)), tz=timezone.utc)
            ni_epoch = datetime(1904, 1, 1, 0, 0, 0, tzinfo=timezone.utc)  # NI reference
            adjusted_data[i] = dt_raw - (platform_epoch - ni_epoch)
        return adjusted_data

    def relative_time(self):
        for channel in self.channels:
            if channel.tag == 'time':
                return channel
            else:
                return False

    def absolute_time(self):
        for channel in self.channels:
            if channel.tag == 'time_abs':
                return channel
            else:
                return False

    def set_time_references(self, time_abs_event):
        absolute_time = self.absolute_time()
        relative_time = self.relative_time()
        if absolute_time:
            absolute_time.data = self.adjust_absolute_time(absolute_time.data)
            relative_time_new = DataChannel.time_channel('relative', transform_data.abs2rel(absolute_time.data))
            if relative_time:
                self.replace_channel(relative_time, relative_time_new)
            else:
                self.add_channel(relative_time_new)
        else:
            if relative_time:
                absolute_time_new = DataChannel.time_channel('absolute',
                                                             transform_data.create_time_abs(relative_time.data,
                                                                                            time_abs_event))
                self.add_channel(absolute_time_new)
            else:
                return 'No time channel found!'

    def find_sample_rate(self):
        relative_time = self.relative_time()
        sample_rate = round(np.diff(relative_time.data).mean())
        return sample_rate

    def is_file_from_daq(self, daq):
        if isinstance(daq, DAQ):
            return daq.has_file(self)
        else:
            print(daq, 'is not a DAQ object.')
        return False


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
