import numpy as np
import matplotlib.pyplot as plt
import lmfit as lm
from helpers import *

path = r'D:\data\20200214\133251_rabi_0dBm_pulse_gap_5000'
# print path+path[16:]+r'.dat'
data = np.loadtxt(path+path[16:]+r'.dat', unpack=True)

no = 201

delay= np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)

# plt.plot(R[0])
# plt.show()

X, _ = rotate(X, Y, zeros = (1800,1999), steady = (1250,1350))
delay = np.array([s[0]/1.8e9 for s in delay])

# np.save(path+r'\rt_norm_X',X)
# plt.imshow(X, aspect='auto',extent=[time[0], time[-1], delay[-1], delay[0]], cmap = 'jet')
# plt.show()
gr = X[0]
ext = X[12]

plt.plot(ext,label = 'ext')
plt.plot(gr,label = 'gr')
plt.legend()
plt.show() 

left = 600
right = 700


def tau_fit(ydata, t ,plot=True):
	# t = delay[:-30]
	# ydata = pop# + np.random.uniform(low=-0.5,high=0.5, size=len(t))
	def expo(tau, norm, rf, shift):
		return norm*np.exp(-t/tau)*np.sin(2*np.pi*rf*t-np.pi*0.5) + shift

	def residual(params):
		p=[]
		for key,value in params.valuesdict().items():
			p.append(value)
		return expo(*p)-ydata

	lmfit_params = lm.Parameters()
	# lmfit_params.add('Frequency', value=0, min=-1, max=1)
	lmfit_params.add('Tau', value=2e-6, min = 1e-6)
	lmfit_params.add('Norm', value=0.5, min = 0.5)
	lmfit_params.add('Rf', value=7e6)
	lmfit_params.add('Shift', value=0.5)
	# print lmfit_params
	mi = lm.minimize(residual,lmfit_params,method='leastsq')
	if plot:
		plt.plot(t/1e-9, ydata, 'o-')
		plt.plot(t/1e-9, mi.residual+ydata)
		plt.xlabel(r'$Time({\mu}s)$')
		plt.ylabel(r'$P_{e}$')
		plt.show()
	return pop, mi.residual+ydata, mi.params['Tau'].value, mi.params['Norm'].value,mi.params['Rf'].value


pop = full_pop(time, X, left, right, ground=gr, excited=ext, order=8)
plt.plot(delay/1e-9, pop, 'o-')
plt.xlabel(r'Time(ns)')
plt.ylabel(r'$P_{e}$')
plt.show()

# _,_,tau,nor,freq1 = tau_fit(pop, delay)
# print(tau)
# print(nor)
# print(freq1/1e6)


# right_arr = range(250,351)
# for index,right in enumerate(right_arr):
# 	print('%d/%d'%(index+1,len(right_arr)))
# 	pops = []
# 	taus = []
# 	left_arr = range(200, right-20)
# 	for index, left in enumerate(left_arr):
# 		pop = full_pop(time, X[:-30], left, right, ground=X[-1], excited=X[0], order=5)
# 		tau = tau_fit(pop, delay[:-30])[-2]
# 		taus.append(tau)
# 	taus = np.array(taus)
# 	plt.plot(left_arr,taus/1e-6, label= right)
# plt.legend()
# plt.show()

# np.savetxt(path+r'\X_data.dat', X , fmt='%0.6f')

	
# X = X[:-30]
# fit_p = tau_fit(True)
# print fit_p[-1], fit_p[-2]