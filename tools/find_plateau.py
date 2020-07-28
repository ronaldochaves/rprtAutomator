# Standard imports
import time as tm

# PyPI imports:
import numpy as np
import matplotlib.pyplot as plt


def find_plateau_central(time_series, threshold, uncertainty=1e-6):
    """
    Implementation of a Centralized Algorithm to find a (the maximum) plateau in an Aggregated Time Series,
    based on the paper (doi = 10.1007/11775300_28).
    In addition, it was introduced an uncertainty variable to make easier to find plateau from real test data.
    """

    # Step 1
    top1 = time_series.max()
    max_index = np.argmax(time_series)
    tau = top1 - threshold
    left_border, right_border = 0, len(time_series) - 1

    # Step 2
    left_border, max_index, tau_l = find_left_plateau(time_series, left_border, max_index, tau)

    # Step 3
    max_index, right_border, tau_r = find_right_plateau(time_series, max_index, right_border, tau)

    # Step 4
    count = 0
    while abs(tau_l - tau_r) > abs(tau_l * uncertainty):
        if tau_l > tau_r:        # Step 5
            max_index, right_border, tau_r = find_right_plateau(time_series, max_index, right_border, tau_l)
            # print('tau_r: {:.2f}'.format(tau_r))
        else:                    # Step 6
            left_border, max_index, tau_l = find_left_plateau(time_series, left_border, max_index, tau_r)
            # print('tau_l: {:.2f}'.format(tau_l))
        count += 1
    tau = tau_l
    return left_border, right_border, max_index, tau


def find_plateau_distrib(time_series, threshold, uncertainty=1e-6):
    """
    Implementation of a Distributed Algorithm to find a (the maximum) plateau in an Aggregated Time Series,
    based on the paper (doi = 10.1007/11775300_28).
    In addition, it was introduced an uncertainty variable to make easier to find plateau from real test data.
    """
    left_border = 0
    right_border = 0
    max_index = 0
    tau = 0
    return left_border, right_border, max_index, tau


def find_left_plateau(time_series, left_border, m, tau):
    for left_pointer in range(left_border, m + 1, 1):
        min_r = min_right(time_series, left_pointer, m)
        max_l = max_left(time_series, left_border, left_pointer)
        if min_r >= max_l and min_r >= tau:
            if left_pointer == left_border:
                tau_l = np.max([tau, time_series[left_pointer]])
            else:
                tau_l = np.max([tau, time_series[left_border:left_pointer].max()])
            # print ('l = {}, m = {}, tau_l = {}'.format(left_pointer, m, tau_l))
            return left_pointer, m, tau_l
    return print('Error: left plateau not found!')


def find_right_plateau(time_series, m, right_border, tau):
    for right_pointer in range(right_border, m - 1, -1):
        min_l = min_left(time_series, m, right_pointer)
        max_r = max_right(time_series, right_pointer, right_border)
        if min_l >= max_r and min_l >= tau:
            if right_pointer == right_border:
                tau_r = np.max([tau, time_series[right_pointer]])
            else:
                tau_r = np.max([tau, time_series[right_pointer + 1:right_border + 1].max()])
            # print ('m = {}, r = {}, tau_r = {}'.format(m, right_pointer, tau_r))
            return m, right_pointer, tau_r
    return print('Error: left plateau not found!')


def min_right(time_series, i, m):
    if i == m:
        return time_series[m]
    else:
        return time_series[i:m + 1].min()


def max_left(time_series, left_border, i):
    if i == left_border:
        return -np.inf
    else:
        return time_series[left_border:i].max()


def min_left(time_series, m, i):
    if i == m:
        return time_series[m]
    else:
        return time_series[m:i + 1].min()


def max_right(time_series, i, right_border):
    if i == right_border:
        return -np.inf
    else:
        return time_series[i + 1:right_border + 1].max()

# Distributed Algorithm to find plateau (Threshold Algorithm by Fagin et al.) #


def main(time_series, threshold, method, uncertainty=1e-6):
    start_time = tm.time()

    print('Started to find plateau via', method, 'method')
    print('...')
    left_border, right_border, max_index, tau = find_plateau_central(time_series, threshold, uncertainty)

    # if method == 'distributed':
    #     left_border, right_border, max_index, tau = find_plateau_distrib(time_series, threshold, uncertainty)
    # elif method == 'centralized':
    #     left_border, right_border, max_index, tau = find_plateau_central(time_series, threshold, uncertainty)
    print('Plateau: (', left_border, ',', right_border, ') - max: %.2f' % time_series[max_index], '- tau: %.2f' % tau)
    print('Plateau found via', method, 'method', '[%.3f seconds]' % (tm.time() - start_time))

    fig = plt.figure('Plateau', figsize=(10, 6), dpi=80)
    plt.plot(time_series, color='red', linewidth=2, marker='s', label='time_series')
    plt.axvline(left_border, color='lightblue', linestyle='-.', label='Plateau_left')
    plt.axvline(right_border, color='darkblue', linestyle='-.', label='Plateau_right')
    plt.hlines(tau, left_border, right_border, color='green', linestyle='--', label='tau')
    plt.legend(loc='upper left')
    plt.grid()
    plt.xlabel("Index")
    plt.ylabel("Time Series")
    plt.draw()

    return left_border, right_border, max_index, tau
