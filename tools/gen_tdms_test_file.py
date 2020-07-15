import os
import math
from datetime import datetime, timezone
import numpy as np
from nptdms import TdmsWriter, RootObject, GroupObject, ChannelObject, timestamp

# Define time epoch (UTC)
test_epoch = datetime(2020, 7, 14, 12, 30, 30, 79060, tzinfo=timezone.utc)
test_epoch_stardard = datetime(1904, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)

test_time = 1

# PXI1_LF
samp_freq = 1000
num_elem = test_time * samp_freq

root_object = RootObject(properties={"rack_name": "PXI1_LF", "sampling_freq": samp_freq})
group_object = GroupObject("group_1")

data_st = np.linspace(0, 1, num_elem, endpoint=True)
ts = (test_epoch - test_epoch_stardard).total_seconds()
data_at = data_st + ts

data_rp = np.heaviside(data_st, 0.25) - np.heaviside(data_st, 0.75)

all_data = [data_st, data_at, data_rp]

tdms_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_inputs')
tdms_name = os.path.join(tdms_path, "rack01_time_stamp.tdms")
with TdmsWriter(tdms_name) as tdms_writer:
    for channel_name, data in zip(['System Time', 'Absolute Time', 'RP101SET'], all_data):
        channel_object = ChannelObject("group_1", channel_name, data, properties={})
        # Write segment
        tdms_writer.write_segment([root_object, group_object, channel_object])
        tdms_writer.write_segment([channel_object])

# PXI2_LF
freq_samp = 1000
num_elem = test_time * freq_samp

root_object = RootObject(properties={"rack_name": "PXI2_LF", "sampling_freq": samp_freq})
group_object = GroupObject("group_1")

data_st = np.linspace(0, 1, num_elem, endpoint=True)
ts = (test_epoch - test_epoch_stardard).total_seconds()
data_at = data_st + ts

data_rp = np.heaviside(data_st, 0.30) - np.heaviside(data_st, 0.85)

all_data = [data_st, data_at, data_rp]

tdms_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_inputs')
tdms_name = os.path.join(tdms_path, "rack02_time_stamp.tdms")
with TdmsWriter(tdms_name) as tdms_writer:
    for channel_name, data in zip(['System Time', 'Absolute Time', 'VE401'], all_data):
        channel_object = ChannelObject("group_1", channel_name, data, properties={})
        # Write segment
        tdms_writer.write_segment([root_object, group_object, channel_object])
        tdms_writer.write_segment([channel_object])

# PXI2_HF
freq_samp = 10000
num_elem = test_time * freq_samp

root_object = RootObject(properties={"rack_name": "PXI2_HF", "sampling_freq": samp_freq})
group_object = GroupObject("group_1")

# ts = (test_epoch - test_epoch_stardard).total_seconds()
# tdms_ts = timestamp.TdmsTimestamp(int(math.floor(ts)), int(math.floor((ts - math.floor(ts))/2**-64)))

data_st = np.linspace(0, 1, num_elem, endpoint=True)
data_rp = np.heaviside(data_st, 0.27) - np.heaviside(data_st, 0.77)

tdms_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_inputs')
tdms_name = os.path.join(tdms_path, "rack02_hf_time_stamp.tdms")
with TdmsWriter(tdms_name) as tdms_writer:
    channel_object = ChannelObject("group_1", "PT501", data_rp, properties={"wf_start_offset": test_epoch,
                                                                            "wf_increment": 1/freq_samp})
    # Write segment
    tdms_writer.write_segment([root_object, group_object, channel_object])
    tdms_writer.write_segment([channel_object])

# HBM_LF
freq_samp = 1200
num_elem = test_time * freq_samp
data_st = np.linspace(0, 1, num_elem, endpoint=True)

['Channel_1_Data', 'Channel_26_Data', 'Channel_33_Data']