# Example running ManFit
import manfit as mf

import numpy as np
import matplotlib.pyplot as plt

# write function with parameters as parameters
path = r'D:\data\20190720\171937_power_dynamic_full_sweep_position_4'
data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)
n = 61
left = 71
right = 121
power= np.array(np.array_split(data[0],n))
freq = np.array_split(data[1],n)[0][left:right]
real = np.array_split(data[2],n)
imag = np.array_split(data[3],n)
absol = np.array_split(data[4],n)
power = power.T[0]

def custom(f, f0, ke1, ke2, ki, norm):
	return norm*np.abs(np.sqrt(ke1*ke2)/(-1j*(f-f0)+(ke1+ke2+ki)/2))

# Initialize Parameters
params = [mf.Parameter(freq[0],freq[-1], name='Frequency'),
		  mf.Parameter(0.1e6,0.6e6, name='ke1'),
		  mf.Parameter(0.5e6,3e6, name='ke2'),
		  mf.Parameter(0.5e6,3e6, name='ki'),
		  mf.Parameter(0.1,1, name='norm')]


i=60
# print(freq)


# setup plot
figure, axes = plt.subplots(1,1,figsize=(6,4), dpi=96)
line2, = axes.plot(freq,absol[i][left:right], 'o')
line1, = axes.plot(freq,custom(freq, *[param.val for param in params]))
# axes.set_ylim(0.25,0.4)
# start ManFit
# mf.manfit(figure, parameter_list, lines_to_update, xdata, ydata, fit_func)
mf.manfit(figure, params, {line1:custom}, freq, absol[i][left:right], custom)



# fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)

# ax.errorbar(power.T[0]-20, (f0/ki)/1e3, fmt='o', yerr = Q_err/1e3 ,capsize=2, elinewidth=1, markeredgewidth=2)
# ax.set_xlabel(r'$Power (dBm)$')
# ax.set_ylabel(r'$Q_{i} (kU)$')
# ax.set_title(path[8:])
# plt.show()