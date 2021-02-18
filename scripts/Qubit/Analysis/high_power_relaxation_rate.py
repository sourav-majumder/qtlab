import numpy as np
import matplotlib.pyplot as plt
from helpers import *


from scipy.constants import hbar
from matplotlib import cm

cons_w = 2*3.14*6.84e9
cons_ke = 2*3.14*1.5e6
cons_k = 2*3.14*2.8e6
cons_delta = 0

def Plin(p):
	return 10.**(p/10.-3.)

def photons(power):
	return Plin(power)/(hbar*cons_w)*(cons_ke/((cons_k/2)**2+cons_delta**2))

path = r'D:\data\20190807\153936_high_power_decay_7oncable'
# print path+path[16:]+r'.dat'
data = np.loadtxt(path+path[16:]+r'.dat', unpack=True)

no = 41

delay= np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)

plt.plot(R[0])
plt.show()
X, _ = rotate(X, Y, zeros = (900,999), steady = (420,460))
delay = np.array([s[0]*4.4e-9 for s in delay])

# np.save(path+r'\rt_norm_X',X)
plt.imshow(X, aspect='auto',extent=[time[0], time[-1], delay[-1], delay[0]], cmap = 'jet')
plt.show()
power = 7
plt.title('(%s dBm drive power on cable) '%power+'photon number %0.e'%photons(power-20-46-3))

for i in range(len(X)):
	plt.plot(time, X[i])
plt.xlabel(r'$\mu s$')
plt.ylabel('Voltage(V)')
# plt.plot(X[0],label = 'ext')
# plt.plot(X[-1],label = 'gr')
# plt.legend()
plt.show() 

# left = 320
# right = 360



# pop = full_pop(time, X, left, right, ground=X[-1], excited=X[0], order=12)
# plt.plot(delay/1e-6, pop)
# plt.show()

# np.savetxt(path+r'\X_data.dat', X , fmt='%0.6f')
# def tau_fit(plot=False):
# 	import lmfit as lm
# 	t = delay
# 	ydata = pop# + np.random.uniform(low=-0.5,high=0.5, size=len(t))
# 	def expo(tau, norm):
# 		return norm*np.exp(-t/tau)

# 	def residual(params):
# 		p=[]
# 		for key,value in params.valuesdict().items():
# 			p.append(value)
# 		return expo(*p)-ydata

# 	lmfit_params = lm.Parameters()
# 	# lmfit_params.add('Frequency', value=0, min=-1, max=1)
# 	lmfit_params.add('Tau', value=3.6e-6)
# 	lmfit_params.add('Norm', value=0.9)
# 	# print lmfit_params
# 	mi = lm.minimize(residual,lmfit_params,method='leastsq')
# 	if plot:
# 		plt.plot(t/1e-6, ydata, '.')
# 		plt.plot(t/1e-6, mi.residual+ydata)
# 		plt.xlabel(r'$Time({\mu}s)$')
# 		plt.ylabel(r'$P_{e}$')
# 		plt.show()
# 	return pop, mi.residual+ydata, mi.params['Tau'].value, mi.params['Norm'].value
	
# # X = X[:-30]
# fit_p = tau_fit(True)
# print fit_p[-1], fit_p[-2]