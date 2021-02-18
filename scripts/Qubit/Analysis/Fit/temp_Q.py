import numpy as np
from fitter import *
left = 130
right = 270


path =[r'D:\data\20190511\154729_power_sweep_7.002MoRe_Al_50mk',
r'D:\data\20190511\160529_power_sweep_7.002MoRe_Al_100mk',
r'D:\data\20190511\162138_power_sweep_7.002MoRe_Al_200mk',
r'D:\data\20190511\164423_power_sweep_7.002MoRe_Al_500mk',
r'D:\data\20190511\171153_power_sweep_7.002MoRe_Al_800mk']

name = '7.002 GHz  MoRe-Al'

temp = [50,100,200,500,800]

n = len(path)
ki = np.array([9.5284e+05,9.6835e+05,9.7947e+05,1.0056e+06,1.0193e+06])#np.zeros(n)
f0 = np.array([7.0038e+09,7.0038e+09,7.0038e+09,7.0038e+09,7.0038e+09] )#np.zeros(n)
ki_err = np.array([2.29e+03,2.59e+03,2.58e+03,2.84e+03,2.72e+03] )#np.zeros(n)
f0_err = np.array([1.17e+03,1.32e+03,1.31e+03,1.41e+03,1.34e+03] )#np.zeros(n)
Q_err = np.zeros(n)

for i in range(n):
	# data_name = path[i]+path[i][16:]+r'.dat'
	# data = np.loadtxt(data_name, unpack=True)
	# freq = data[1][left:right]
	# real = data[2]
	# imag = data[3]
	# absol = data[4][left:right]
	# f = Fitter(custom)
	# result = f.fit(freq, absol, print_report = True)
	# f.plot()
	# ki[i] = result.params['ki'].value
	# f0[i] = result.params['f0'].value
	# ki_err[i] = result.params['ki'].stderr
	# f0_err[i] = result.params['f0'].stderr
	Q_err[i] = (f0_err[i]/f0[i] + ki_err[i]/ki[i])*(f0[i]/ki[i])

fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)

ax.errorbar(temp, (f0/ki)/1e3, fmt='o', yerr = Q_err/1e3 ,capsize=2, elinewidth=1, markeredgewidth=2)
ax.set_xlabel(r'$T (mK)$')
ax.set_ylabel(r'$Q_{i} (kU)$')
ax.set_title(name)
plt.show()


# fr.fit(freq, real[-1], print_report = True)
# fr.plot()
# fm.fit(freq, imag[-1], print_report = True)
# fm.plot()
