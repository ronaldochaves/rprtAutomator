import os
from datetime import datetime, timedelta, timezone
import numpy as np
from nptdms import TdmsWriter, RootObject, GroupObject, ChannelObject

root_object = RootObject(properties={"prop1": "Rian", "prop2": 3})
group_object = GroupObject("group_1", properties={"prop1": 1.2345, "prop2": False})

num_elem = 1000
data_st = np.linspace(0, 1, num_elem, endpoint=True)
ts = (datetime.now() - datetime(1904, 1, 1)).total_seconds()
data_at = data_st + ts
print(type(data_at[0]))
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
