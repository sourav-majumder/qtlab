import numpy as np
import matplotlib.pyplot as plt
import lmfit as lm

g01 = 72.88e6
delta = -761.93e6
chi01 = -6.972e6
Ec = 117e6

chi = -(chi01*Ec)/(delta-Ec)
# print(chi/1e6)

def Plin(p):
	return 10.**(p/10.-3.)

def photons(power):
	return Plin(power)/(hbar*w)*(ke/((k/2)**2+delta**2))


path = r'D:\data\20190828\121353_two_tone_6.003792_probe'

data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)

n = 11
power= np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]
absol = np.array_split(data[4],n)


freq_array = np.zeros(n)
power_array = np.zeros(n)
for i in range(n):
	arg = np.argmin(absol[i])
	freq_array[i] = freq[arg]
	power_array[i] = power[i][0]


bare_qubit = freq_array[0]
freq = freq_array-bare_qubit
# for i in range(len(freq)):
# 	freq[i] = freq[i]/(2*(i+1))

# print(np.average(freq))
#################
#Stark-Shift Frequency Plot
#################
t = Plin(power_array)
ydata = freq/(2*chi)

def linear(norm):
	return norm*t

def residual(params):
	p=[]
	for key,value in params.valuesdict().items():
		p.append(value)
	return linear(*p)-ydata

lmfit_params = lm.Parameters()
# lmfit_params.add('Frequency', value=0, min=-1, max=1)
# lmfit_params.add('Shift', value=0)
lmfit_params.add('Norm', value=25)
# print lmfit_params
mi = lm.minimize(residual,lmfit_params,method='leastsq')
plt.plot(t/1e-6, ydata, 'o')
plt.plot(t/1e-6, mi.residual+ydata)
plt.xlabel(r'Power ($\mu$Watt)')
plt.ylabel(r'Photon')
print(lm.fit_report(mi))
print(mi.params['Norm'].value)

multi_factor = mi.params['Norm'].value
print(multi_factor)
plt.show()

