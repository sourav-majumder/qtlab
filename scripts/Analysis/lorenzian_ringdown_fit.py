import numpy as np
from lmfit import *

def lorentzian(freq_arr, amp, x0, gamma):
	return amp/(np.pi*gamma*(1+((freq_arr-x0)/gamma)**2))

def residual(params):
	p = []
	for key,value in params.valuesdict().items():
		p.append(value)
	return lorentzian(freq_arr, *p) - y

datadir = r'D:\data\20170609\162009_2port_copper_50ns'

datfilename = datadir.split('\\')[-1]
filestr = '%s\%s' % (datadir, datfilename)

# d = np.loadtxt(filestr+'.dat')

# numpoints = 1000

# time_slice = 550

# x_arr =  d[time_slice::numpoints, 2]
# y_arr =  d[time_slice::numpoints, 3]
# freq_arr = d[time_slice::numpoints, 0]

# np.save(filestr+'_freq_arr', freq_arr)
# np.save(filestr+'_x_arr', x_arr)
# np.save(filestr+'_y_arr', y_arr)

freq_arr = np.load(filestr+'_freq_arr.npy')
x_arr = np.load(filestr+'_x_arr.npy')
y_arr = np.load(filestr+'_y_arr.npy')

# x_arr[606] = x_arr[605]
# x_arr[607:] /= x_arr[607]
# x_arr[607:] *= x_arr[605]
# x_arr = x_arr**2

# y_arr[606] = y_arr[605]
# y_arr[607:] /= y_arr[607]
# y_arr[607:] *= y_arr[605]

initial = [0.03, 7.978e9, 1e6]

params = Parameters()

params.add_many(('amplitude',	initial[0],		True,	None,	None,		None),
				('x0',			initial[1],		True,	None,	None,		None),
				('gamma',		initial[2],		True,	None,	None,		None),)

y = x_arr**2 + y_arr**2
mi = minimize(residual, params, method='leastsq')
print fit_report(mi)