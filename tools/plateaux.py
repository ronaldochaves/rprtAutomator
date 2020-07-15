# PyPI imports:
import numpy as np
import matplotlib.pyplot as plt

# Local imports:
from tools import createdocument


def find_plateau(time_series, epson, uncert=1e-6):
    """
    Implementation of a Centralized Algorithm to find a (the maximum) plateau in an Aggregated Time Series,
    based on the paper (doi = 10.1007/11775300_28).
    In addition, it was introduced an uncertainty variable to make easier to find plateau from real test data.
    """
    
    # Step 1
    top1 = time_series.max()
    max_index = np.argmax(time_series)
    tau = top1 - epson
    left_border, right_border = 0, len(time_series) - 1

    # Step 2
    left_border, max_index, tau_l = find_left_plateau(time_series, left_border, max_index, tau)
    
    # Step 3
    max_index, right_border, tau_r = find_right_plateau(time_series, max_index, right_border, tau)
    
    # Step 4
    count = 0
    while abs(tau_l - tau_r) > abs(tau_l*uncert):
        if tau_l > tau_r:        # Step 5
            max_index, right_border, tau_r = find_right_plateau(time_series, max_index, right_border, tau_l)
            # print('tau_r: {:.2f}'.format(tau_r))
        else:                    # Step 6
            left_border, max_index, tau_l = find_left_plateau(time_series, left_border, max_index, tau_r)
            # print('tau_l: {:.2f}'.format(tau_l))
        count += 1
    tau = tau_l
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
            # print ('l = {}, m = {}, tau_l = {}'.format(l, m, tau_l))
            return left_pointer, m, tau_l
    return print('Error: left plateau not found!')


def find_right_plateau(time_series, m, right_border, tau):
    for r in range(right_border, m - 1, -1):
        min_l = min_left(time_series, m, r)
        max_r = max_right(time_series, r, right_border)
        if min_l >= max_r and min_l >= tau:
            if r == right_border:
                tau_r = np.max([tau, time_series[r]])
            else:
                tau_r = np.max([tau, time_series[r + 1:right_border + 1].max()])
            # print ('m = {}, r = {}, tau_r = {}'.format(m, r, tau_r))
            return m, r, tau_r
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


# Test case
if __name__ == '__main__':
    # A = np.array([1, 5, 0, 4, 7, 3, 6, 8, 10, 12, 9, 2])
    A = np.array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0])
    # A = np.array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5])
    # A = np.array([3, 3, 5, 3, 3, 0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5])
    # A = np.array([3, 3, 5, 3, 3, 0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5, 6])
    # A = np.array([6, 3, 3, 5, 3, 3, 0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5,
    #              6])
    
    epson_ = 0.5
    freq = 1                # Sample rate
    plateau_l, plateau_r, m_, tau_ = find_plateau(A, epson_)

    print('Plateau: (', plateau_l, ',', plateau_r, ') - max: %.2f' % A[m_],  '- tau: %.2f' % tau_,
          '- plat_time = %.3f s' % ((plateau_r - plateau_l) / freq))

    fig = plt.figure('Debug-Plateau', figsize=(10, 6), dpi=80)
    plt.plot(A, color='red', linewidth=2, marker='s', label='A')
    plt.axvline(plateau_l, color='lightblue', linestyle='-.', label='Plateau_left')
    plt.axvline(plateau_r, color='darkblue', linestyle='-.', label='Plateau_right')
    plt.hlines(tau_, plateau_l, plateau_r, color='green', linestyle='--', label='tau')
    plt.legend(loc='upper left')
    plt.grid()
    plt.xlabel("Index")
    plt.ylabel("Aggregated Time Series")
    plt.draw()
