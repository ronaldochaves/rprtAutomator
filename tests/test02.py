# Standard imports
import hashlib
import os

# PyPI imports
import matplotlib.pyplot as plt
import numpy as np

# Local imports
import plateaux
from tools import createdocument

# Define test input
time_series = np.array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0])
epson = 0.5
freq = 1  # Sample rate

# Execute function under test
plateau_l, plateau_r, max_index, tau = plateaux.find_plateau(time_series, epson)

print('Plateau: (', plateau_l, ',', plateau_r, f') - max: %.2f' % time_series[max_index], '- tau: %.2f' % tau,
      '- plat_time = %.3f s' % ((plateau_r - plateau_l) / freq))

fig = plt.figure('Debug-Plateau', figsize=(10, 6), dpi=80)
plt.plot(time_series, color='red', linewidth=2, marker='s', label='A')
plt.axvline(plateau_l, color='lightblue', linestyle='-.', label='Plateau_left')
plt.axvline(plateau_r, color='darkblue', linestyle='-.', label='Plateau_right')
plt.hlines(tau, plateau_l, plateau_r, color='green', linestyle='--', label='tau')
plt.legend(loc='upper left')
plt.grid()
plt.xlabel("Index")
plt.ylabel("Aggregated Time Series")
plt.draw()

doc = createdocument.ReportDocument(title='run example plateaux.py', file_name_prefix='run_example_plateaux',
                                    user_name='Test Function')
doc.add_heading("Here is an example level 3 header", level=3)
doc.add_paragraph("Here is the figure:")
doc.add_fig()
doc.finish()
print("figure added to ", doc.file_name)
