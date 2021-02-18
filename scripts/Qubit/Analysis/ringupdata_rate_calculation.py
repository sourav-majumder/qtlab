import numpy as np
import matplotlib.pyplot as plt
from helpers import *

path = r'D:\data\20190804\121119_low_power_cavity_data'
# print path+path[16:]+r'.dat'
data = np.loadtxt(path+path[16:]+r'.dat', unpack=True)

no = 1

time = np.array_split(data[0],no)[0]/1e-6
X = np.array_split(data[1],no)
Y = np.array_split(data[2],no)
R = np.array_split(data[3],no)

plt.plot(X[0],Y[0], '.')
plt.xlim([-0.3,+0.3])
plt.ylim([-0.3,+0.3])
plt.grid()
plt.show()
X, _ = rotate(X, Y, zeros = (900,999), steady = (620,720))

# np.save(path+r'\rt_norm_X',X)
plt.plot(X[0])
plt.yscale('log')
plt.show()

left = 230
right = 260

np.savetxt(path+r'\X_data.dat', X , fmt='%0.6f')
def tau_fit(plot=False):
	import lmfit as lm
	t = time[left:right]-time[left]
	ydata = X[0][left:right]
	def expo(tau, norm):
		return norm*(1-np.exp(-t/tau))

	def residual(params):
		p=[]
		for key,value in params.valuesdict().items():
			p.append(value)
		return expo(*p)-ydata

	lmfit_params = lm.Parameters()
	# lmfit_params.add('Frequency', value=0, min=-1, max=1)
	lmfit_params.add('Tau', value=10e-6)
	lmfit_params.add('Norm', value=0.9)
	# print lmfit_params
	mi = lm.minimize(residual,lmfit_params,method='leastsq')
	if plot:
		plt.plot(t, ydata, '.')
		plt.plot(t, mi.residual+ydata,'o-')
		plt.xlabel(r'$Time({\mu}s)$')
		plt.ylabel(r'$voltage$')
		plt.show()
	return mi.params['Tau'].value, mi.params['Norm'].value
	
# X = X[:-30]
fit_p = tau_fit(True)
print fit_p[0], fit_p[1]