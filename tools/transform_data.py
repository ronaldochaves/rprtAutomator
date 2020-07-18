# Standard imports
import csv
import math
import os
import time as tm
from datetime import datetime, timezone, timedelta

# PyPI imports
import numpy as np
import scipy.io as sio
from nptdms import TdmsFile
from scipy.interpolate import interp1d


# Trim out size-specified borders from data
def trim(var_data, trim_ratio):
    border_size = math.floor(len(var_data) * trim_ratio)
    return var_data[border_size:-border_size]


project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_input = os.path.join(project_dir, 'tests', 'test_outputs')
data_dir_output = os.path.join(project_dir, 'tests', 'test_outputs')
trim_factor = 0.05

# Pick test suite
csv_files = []
for entry in sorted(os.scandir(data_dir_input), key=lambda ent: ent.name):
    if entry.is_file() and entry.name.endswith('_extracted.csv') and not entry.name.startswith('.'):
        csv_files.append(entry.path)
print(csv_files)

# load data
data = {}
for file in csv_files:
    with open(file) as f:
        reader = csv.DictReader(f)
        print(reader)
        # for row in reader:
        #     key = row[0]
        #     data[key] = row[1:]
        #     print(data)
        #     print(row['first_name'], row['last_name'])
