# To be run in scripts folder

import numpy as np
import progressbar
import matplotlib.pyplot as plt
from lmfit import *

from constants import *

def residual(params):
	p = []
	for key,value in params.valuesdict().items():
		p.append(value)
	# return ringdown_func(timearr, *p) - y
	return p[0]*exp_fall(timearr, p[1])*np.cos(f - freq_arr[500]) - y

datadir = r'D:\data\20170609\162009_2port_copper_50ns'

datfilename = datadir.split('\\')[-1]
filestr = '%s\%s' % (datadir, datfilename)

timearr_full = np.load(filestr+'_timearr.npy')[:-15]
I_arr = np.load(filestr+'_corrected_I.npy')
Q_arr = np.load(filestr+'_corrected_Q.npy')
freq_arr = np.load(filestr+'_freq_arr.npy')

# plt.plot(I_arr[500])

# initial=[init_time,	init_const,	exp_const,	tc,		pulse_length]
initial = [0.88*us,		1.059e-12,		1e-11,		70*ns,	1.09*us, freq_arr[500], np.pi]

# deconvx_fit = []
# deconvx_disp = []

tc_arr = []
tc_err = []

bar = progressbar.ProgressBar(maxval=1001, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
bar.start()

index = 0
while index <1001:
	bar.update(index)
	left = 620
	right = 680
	y = I_arr[index][left:right]
	# plt.plot(y)
	# plt.show()
	f = freq_arr[index]
	timearr = timearr_full[left:right]-timearr_full[left]
	total_time = timearr[-1] - timearr[0]


	params = Parameters()

	#					Name			Init value		Vary?	Min			Max			Expr
	params.add_many(#('init_time',		initial[0],		True,	0,			1*us,		None),
					#('init_const',		initial[1],		True,	1e-14,		1e-10,		None),
					('exp_const',		initial[2],		True,	1e-14,		1e-9,		None),
					('tc',				initial[3],		True,	1*ns,		300*ns,		None))
					#('w0',				initial[5],		False,	7.8*GHz,	8.2*GHz,	None),
					#('phi',				initial[6],		True,	0,			2*np.pi,	None))#,
					#('pulse_length',	initial[4],		True,	0.5*us,		2.1*us,		None))#,
					# ('init_pulse',		initial[0]+initial[4],			True,	None,		total_time,	'pulse_length+init_time'))

	mi = minimize(residual, params, method='leastsq')
	# print fit_report(mi)
	index += 1

	tc_arr.append(mi.params['tc'])
	tc_err.append(mi.params['tc'].stderr)

	plt.plot(timearr, residual(mi.params)+y, 'b')
	plt.plot(timearr, y, color='#FF0000BB')
	plt.show()

	# deconvx_fit.append(residual(mi.params)+y)
	# deconvx_disp.append(y)

bar.finish()

plt.plot(freq_arr, tc_arr, 'bo', markersize=1)#, yerr=tc_err)
plt.show()

# tc_arr = []
# tc_err = []

# index = 0
# while index < 1001:
# 	left = 630
# 	right = 690
# 	y = deconvy_arr[index][left:right]
# 	timearr = timearr_full[left:right]-timearr_full[left]
# 	total_time = timearr[-1] - timearr[0]


# 	params = Parameters()

# 	#					Name			Init value		Vary?	Min			Max			Expr
# 	params.add_many(#('init_time',		initial[0],		True,	0,			1*us,		None),
# 					#('init_const',		initial[1],		True,	1e-14,		1e-10,		None),
# 					('exp_const',		initial[2],		True,	1e-12,		2e-10,		None),
# 					('tc',				initial[3],		True,	1*ns,		300*ns,		None),
# 					('w0',				initial[5],		True,	7.8*GHz,	8.2*GHz,	None),
# 					('phi',				initial[6],		True,	0,			2*np.pi,	None))#,
# 					#('pulse_length',	initial[4],		True,	0.5*us,		2.1*us,		None))#,
# 					# ('init_pulse',		initial[0]+initial[4],			True,	None,		total_time,	'pulse_length+init_time'))

# 	mi = minimize(residual, params, method='leastsq')
# 	# print fit_report(mi)
# 	index += 1

# 	tc_arr.append(mi.params['tc'])
# 	tc_err.append(mi.params['tc'].stderr)

# 	# plt.plot(timearr, residual(mi.params)+y, 'b')
# 	# plt.plot(timearr, y, color='#FF0000BB')
# 	# plt.show()

# 	# deconvx_fit.append(residual(mi.params)+y)
# 	# deconvx_disp.append(y)

# plt.errorbar(freq_arr, tc_arr)#, yerr=tc_err)
# plt.show()
# disp = np.array(deconvx_disp)
# fit = np.array(deconvx_fit)
# f, axarr = plt.subplots(2)
# axarr[0].imshow(disp/disp.max(), aspect='auto')
# axarr[1].imshow(fit/fit.max(), aspect='auto')
# plt.show()