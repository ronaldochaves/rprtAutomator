# PyPI imports
import matplotlib.pyplot as plt
import numpy as np

# Local imports
from tools import createdocument, find_plateau

# Define test input
time_series = np.array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0])
epson = 0.5
freq = 1  # Sample rate

# Execute function under test
print('Started testing find_plateau.py')

left_border, right_border, max_index, tau = find_plateau(time_series, epson, 'centralized')
print('Plateau: (', left_border, ',', right_border, ') - max: %.2f' % time_series[max_index], '- tau: %.2f' % tau,
      '- plat_time = %.3f' % ((right_border - left_border) / freq))

print('Finished testing find_plateau.py')

fig = plt.figure('Debug-Plateau', figsize=(10, 6), dpi=80)
plt.plot(time_series, color='red', linewidth=2, marker='s', label='A')
plt.axvline(left_border, color='lightblue', linestyle='-.', label='Plateau_left')
plt.axvline(right_border, color='darkblue', linestyle='-.', label='Plateau_right')
plt.hlines(tau, left_border, right_border, color='green', linestyle='--', label='tau')
plt.legend(loc='upper left')
plt.grid()
plt.xlabel("Index")
plt.ylabel("Aggregated Time Series")
plt.draw()

doc = createdocument.ReportDocument(title='Here is a title', file_name_prefix='report_test02_v',
                                    user_name='Test Function')
doc.add_heading("Here is an example level 3 header", level=3)
doc.add_paragraph("Here is the figure:")
doc.add_fig()
print("Figure added to", doc.file_name)
doc.finish()
