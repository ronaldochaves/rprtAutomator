# Headers
import numpy as np
import matplotlib.pyplot as plt

def find_plateau(A, epson, uncert = 1e-6):
	"""
	Implementation of a Centralized Algorithm to find a (the maximum) plateau in an Aggregated Time Series,
	based on the paper (doi = 10.1007/11775300_28).
	In addition, it was introduced an uncertanty variable to make easier to find plateau from real test data.
	"""
	
	# Step 1
	top1 = A.max()
	m = np.argmax(A)
	print(m)
	tau = top1 - epson
	L, R = 0, len(A) - 1

	# Step 2
	l, m, tau_l = find_left_plateau(A, L, m, tau)
	
	# Step 3
	m, r, tau_r = find_right_plateau(A, m, R, tau)
	
	# Step 4
	L, R = l, r
	count = 0
	while abs((tau_l - tau_r)/tau_l) > uncert:
		print(abs((tau_l - tau_r)/tau_l))
		if tau_l > tau_r:		# Step 5
			m, r, tau_r = find_right_plateau(A, m, R, tau_l)
			print('tau_r: {:.2f}'.format(tau_r))
		else:					# Step 6
			l, m, tau_l = find_left_plateau(A, L, m, tau_r)
			print('tau_l: {:.2f}'.format(tau_l))
		L, R = l, r 			# Step 4
		count += 1
	tau = tau_l
	print(count)
	return L, R, m, tau

def find_left_plateau(A, L, m, tau):
	for l in range(L, m + 1, 1):
		min_r = min_right(A, l, m)
		max_l = max_left(A, L, l, m)
		if min_r >= max_l and min_r >= tau:
			if l == L:
				tau_l = np.max([tau, A[l]])
			else:
				tau_l = np.max([tau, A[L:l].max()])
			print ('l = {}, m = {}, tau_l = {}'.format(l, m, tau_l))
			return l, m, tau_l
	return print('Error: left plateau not found!')

def find_right_plateau(A, m, R, tau):
	for r in range(R, m - 1, -1):
		min_l = min_left(A, m, r)
		max_r = max_right(A, m, r, R)
		if min_l >= max_r and min_l >= tau:
			if r == R:
				tau_r = np.max([tau, A[r]])
			else:
				tau_r = np.max([tau, A[r + 1:R + 1].max()])
			print ('m = {}, r = {}, tau_r = {}'.format(m, r, tau_r))
			return m, r, tau_r
	return print('Error: left plateau not found!')

def min_right(A, i, m):
	if i == m:
		return A[m]
	else:
		return A[i:m + 1].min()

def max_left(A, L, i, m):
	if i == L:
		return -np.inf
	else:
		return A[L:i].max()

def min_left(A, m, i):
	if i == m:
		return A[m]
	else:
		return A[m:i + 1].min()

def max_right(A, m, i, R):
	if i == R:
		return -np.inf
	else:
		return A[i + 1:R + 1].max()

# Distributed Algorithm ro find plateau (Threshold Algorithm by Fagin et al.) #


# Test case
if __name__ == '__main__':
	# A = np.array([1, 5, 0, 4, 7, 3, 6, 8, 10, 12, 9, 2])
	A = np.array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0])
	# A = np.array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5])
	# A = np.array([3, 3, 5, 3, 3, 0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5])
	# A = np.array([3, 3, 5, 3, 3, 0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5, 6])
	# A = np.array([6, 3, 3, 5, 3, 3, 0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 3, 2, 1, 0, 5, 5, 5, 5, 5 ,5, 5, 6])
	
	epson = 0.5
	freq = 1				# Sample rate
	plateau_l, plateau_r, m, tau = find_plateau(A, epson)

	print('Plateau: ({}, {}) - max: {:.2f} - tau: {:.2f} - plat_time = {:.3f}s'.format(plateau_l, plateau_r, A[m], tau, (plateau_r - plateau_l)/freq))

	fig = plt.figure('Debug-Plateau', figsize = (10, 6), dpi = 80)
	plt.plot(A, color = 'red', linewidth = 2, marker = 's', label = 'A')
	plt.axvline(plateau_l, color = 'lightblue', linestyle = '-.', label = 'Plateau_left')
	plt.axvline(plateau_r, color = 'darkblue', linestyle = '-.', label = 'Plateau_right')
	plt.hlines(tau, plateau_l, plateau_r, color = 'green', linestyle = '--', label = 'tau')
	plt.legend(loc = 'upper left')
	plt.grid()
	plt.xlabel("Index")
	plt.ylabel("Aggregated Time Series")
	plt.show()