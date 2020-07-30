# Standard imports
import os
import numpy as np

# Path
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
txt_path = os.path.join(project_dir, 'tests', 'test_inputs')
txtfile = os.path.join(txt_path, 'example_txtfile.txt')

line = 'ch<var>channel</var>;<var>pos</var>'
channels = ['P_1', 'P_2', 'P_3', 'P_4', 'P_5']

time = np.arange(0, 1e3, 1e-3)
P_1 = time + 1
P_2 = time + 2
P_3 = time + 3
P_4 = time + 4
P_5 = time + 5

with open(txtfile, 'w') as txt:
    for i, channel in enumerate(channels):
        txt.write(line + '\n')
        txt.write('ch' + str(i + 1) + ';' + channel + '\n')
    header = 'x[s]'
    for i in range(len(channels)):
        header += '\ty,ch' + str(i) + '[bar]'
    txt.write(header + '\n\n')

    for i in range(len(time)):
        segment = ' ' + '%.6f' % (time[i])
        for j, channel in enumerate(channels):
            segment += '\t ' + '%.6f' % (time[i] + j)
        txt.write(segment + '\n')
