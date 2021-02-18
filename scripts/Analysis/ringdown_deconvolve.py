# To be run in scripts folder

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

from constants import *

d = np.loadtxt(r'D:\data\20170609\162009_2port_copper_50ns\162009_2port_copper_50ns.dat').swapaxes(0,1)

numpoints = 1000
numfreqs = d.shape[1]/numpoints

datano = 0
deconvx_arr = []
deconvy_arr = []

while datano < numfreqs:
	freq = d[0][datano*numpoints]
	timearr = d[1][datano*numpoints:(datano+1)*numpoints]
	datax = [timearr, d[2][datano*numpoints:(datano+1)*numpoints]]
	datay = [timearr, d[3][datano*numpoints:(datano+1)*numpoints]]

	deconvx, _ = deconvolve(datax, 49.7*ns, 1)
	deconvx_arr.append(deconvx)
	deconvy, _ = deconvolve(datay, 49.7*ns, 1)
	deconvy_arr.append(deconvy)

	# save it

	# np.save('deconv%d' % datano, deconvx)
	np.save(r'D:\data\20170609\162009_2port_copper_50ns\162009_2port_copper_50ns_timearr', timearr[:len(deconvx)])

	# fit it
	# result = opt.curve_fit(ringdown_func, timearr[:len(deconvx)], deconvx)

	# # plot it
	# plt.yscale('log')
	# plt.plot(timearr[:len(deconvx)], deconvx)
	# plt.show()
	datano+=1


np.save(r'D:\data\20170609\162009_2port_copper_50ns\162009_2port_copper_50ns_deconvoluted_x', np.array(deconvx_arr))
np.save(r'D:\data\20170609\162009_2port_copper_50ns\162009_2port_copper_50ns_deconvoluted_y', np.array(deconvy_arr))