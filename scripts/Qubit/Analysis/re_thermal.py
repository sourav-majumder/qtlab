import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import polyfit, polyval, polyder
from helpers import *

path = r'D:\data\20190520\182344_re_thermal_pow_sweep_#7'
# print path+path[16:]+r'.dat'
data = np.loadtxt(path+path[16:]+r'.dat', unpack=True)

no = 101

delay= np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]#/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)


X, _ = rotate(X, Y, zeros = (1900,1999), steady = (1350,1450))
delay = np.array([s[0]*1e-6 for s in delay])
plt.plot(Y[0])
plt.plot(X[0])
plt.show()
left = 550
right = 1050
plot = False

re_ther = np.zeros(no)

for i in range(no):
	import lmfit as lm
	t = time[left:right]
	ydata = X[i][left:right]
	def expo(tau, norm,a):
		return norm*(a-np.exp(-t/tau))

	def residual(params):
		p=[]
		for key,value in params.valuesdict().items():
			p.append(value)
		return expo(*p)-ydata

	lmfit_params = lm.Parameters()
	# lmfit_params.add('Frequency', value=0, min=-1, max=1)
	lmfit_params.add('Tau', value=1e-6)
	lmfit_params.add('Norm', value=0.9)
	lmfit_params.add('a', value=1)
	# print lmfit_params
	mi = lm.minimize(residual,lmfit_params,method='leastsq')
	if plot:
		plt.plot(t/1e-6, ydata, '.')
		plt.plot(t/1e-6, mi.residual+ydata)
		plt.show()
	re_ther[i] =  1/mi.params['Tau'].value#, mi.params['Norm'].value

plt.plot(delay/1e-6, re_ther/1e6)
plt.ylim(0.25,2.7)
plt.show()
