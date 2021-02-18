import numpy as np
from fitter import *
from scipy.constants import hbar


cons_w = 2*3.14*6.002e9
cons_ke = 2*3.14*0.017e6
cons_k = 2*3.14*1.4e6
cons_delta = 0

def Plin(p):
	return 10.**(p/10.-3.)

def photons(power):
	return Plin(power)/(hbar*cons_w)*(cons_ke/((cons_k/2)**2+cons_delta**2))


path = r'D:\data\20200223\074606_Power_Sweep_229mV'
data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)
n = 27
power= np.array(np.array_split(data[0],n))
freq = np.array_split(data[1],n)[0]
real = np.array_split(data[2],n)
imag = np.array_split(data[3],n)
absol = np.array_split(data[4],n)

f = Fitter(S21r)
# fr = Fitter(custom_real)
# fm = Fitter(custom_imag)
# plt.plot(np.real(d.data),np.imag(d.data))
# plt.show()
k = np.zeros(n)
f0 = np.zeros(n)
Q = np.zeros(n)
k_err = np.zeros(n)
f0_err = np.zeros(n)
Q_err = np.zeros(n)
left1 = 151
right1 = 246
for i in range(11):
	result = f.fit(freq[left1:right1], absol[i][left1:right1], print_report = True)
	# f.plot()
	k[i] = np.abs(result.params['k'].value)
	f0[i] = result.params['f0'].value
	Q[i] = f0[i]/k[i]
	k_err[i] = result.params['k'].stderr
	f0_err[i] = result.params['f0'].stderr
	Q_err[i] = (f0_err[i]/f0[i] + k_err[i]/k[i])*(f0[i]/k[i])

left = 81
right = 141

for i in range(20,27):
	result = f.fit(freq[left:right], absol[i][left:right], print_report = True)
	# f.plot()
	k[i] = np.abs(result.params['k'].value)
	f0[i] = result.params['f0'].value
	Q[i] = f0[i]/k[i]
	k_err[i] = result.params['k'].stderr
	f0_err[i] = result.params['f0'].stderr
	Q_err[i] = (f0_err[i]/f0[i] + k_err[i]/k[i])*(f0[i]/k[i])

# power = np.delete(power.T[0],[35])
# Q = np.delete(Q,[35])
# Q_err = np.delete(Q_err,[35])
# k = np.delete(k,[35])
# k_err = np.delete(k_err,[35])

# print(power)
fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
ax.errorbar(photons(power.T[0]-80), Q/1e3, fmt='.', yerr = Q_err/1e3 ,capsize=2, elinewidth=1, markeredgewidth=2)
# ax.plot(power.T[0],(f0/ki)/1e3)
ax.set_xlabel(r'Photon number')
ax.set_ylabel(r'Q (kU)')
ax.set_xscale('log')
ax.set_title(path[8:])
plt.show()

# fig1, ax1 = plt.subplots(nrows=1, ncols=1, sharex=True)
# ax1.errorbar(photons(power.T[0]-80), k/1e6, fmt='.', yerr = k_err/1e6 ,capsize=2, elinewidth=1, markeredgewidth=2)
# # ax.plot(power.T[0],(f0/ki)/1e3)
# ax1.set_xlabel(r'Photon number')
# ax1.set_ylabel(r'Linewidth (MHz)')
# ax1.set_xscale('log')
# ax1.set_title(path[8:])
# plt.show()

# np.savetxt(r'D:\data\20200217\Analysis_quality_factor\500M_below_cavity_229.txt', (photons(power.T[0]-80), k/1e6, k_err/1e6, Q/1e3, Q_err/1e3))

# fr.fit(freq, real[-1], print_report = True)
# fr.plot()
# fm.fit(freq, imag[-1], print_report = True)
# fm.plot()
