import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import hbar, pi
from lmfit import Model, fit_report

#plt.style.use('presentation.mplstyle')

def photon(power):
	p = 1e-3*10**(power/10.)
	return (p*ke)/(hbar*w*((k/2)**2+(w-w0)**2))

def line(x, m, c):
	return m*x + c

attenuation = 52 #dB
k = 2*pi*513e3
ke = 0.7*k
w0 = 2*pi*6.310792e9

#######################

w = w0 - (2*pi*5.2656*1e6)
pth = 'D:\\data\\2018-09-08\\12-06-01_omit_pump_pw_sw_mode1\\'
file = 'gamma_vs_pw.dat'

###################


power, cp, gamm = np.loadtxt(pth+file, unpack=True)

photons = photon(power-attenuation)
plt.figure(figsize = (5,3))
plt.plot(photons,cp, '-ro')
plt.xlabel('number of photons', fontsize=12)
plt.ylabel(r'Cooperativity', fontsize = 12)
plt.grid()
# plt.plot(photons, coop, '.')
#plt.xscale('log')
# plt.title(r'Cooperativity vs Number of Cavity Photons', fontsize=20)
plt.tight_layout()
plt.savefig(pth+'Cp_number_ph.png', transparent=True)
#plt.show()