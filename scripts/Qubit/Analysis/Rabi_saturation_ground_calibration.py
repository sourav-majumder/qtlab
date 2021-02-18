import numpy as np
import matplotlib.pyplot as plt
import lmfit as lm
from helpers import *


#path_gr = r'D:\data\20201219\193651_dimon_ground\193651_dimon_ground'
# print path+path[16:]+r'.dat'

data_gr = np.loadtxt(r'D:\data\20201221\145146_Dimon_dark_ground\145146_Dimon_dark_ground.dat', unpack=True, skiprows = 23)

no_gr = 11

delay_gr = np.array_split(data_gr[0],no_gr)
time_gr = np.array_split(data_gr[1],no_gr)[0]/1e-6
X_gr = np.array_split(data_gr[2],no_gr)
Y_gr = np.array_split(data_gr[3],no_gr)
R_gr = np.array_split(data_gr[4],no_gr)

#plt.plot(R_gr[0])
#plt.show()

X_gr, _ = rotate(X_gr, Y_gr, zeros = (900,1000), steady =  (700,800))



#path_sat = r'D:\data\20201219\193450_dimon_saturation\193450_dimon_saturation'
# print path+path[16:]+r'.dat'
data_sat = np.loadtxt(r'D:\data\20201221\152012_Dimon_dark_saturation\152012_Dimon_dark_saturation.dat', unpack=True, skiprows = 23)

no_sat = 11

delay_sat = np.array_split(data_sat[0],no_sat)
time_sat = np.array_split(data_sat[1],no_sat)[0]/1e-6
X_sat = np.array_split(data_sat[2],no_sat)
Y_sat = np.array_split(data_sat[3],no_sat)
R_sat = np.array_split(data_sat[4],no_sat)

#plt.plot(R_sat[0])
#plt.show()

X_sat, _ = rotate(X_sat, Y_sat, zeros = (900,1000), steady =  (700,800))



#path = r'D:\data\20201219\185435_rabi_dimon_long\185435_rabi_dimon_long'
# print path+path[16:]+r'.dat'
data = np.loadtxt(r'D:\data\20201224\003024_Dark_driven_bright_pi_cal\003024_Dark_driven_bright_pi_cal.dat', unpack=True, skiprows = 23)

no = 61

delay1 = np.array_split(data[0],no)
time = np.array_split(data[1],no)[0]/1e-6
X = np.array_split(data[2],no)
Y = np.array_split(data[3],no)
R = np.array_split(data[4],no)

#plt.plot(R[0])
#plt.show()

X, _ = rotate(X, Y, zeros = (900,1000), steady = (700,800))
delay = np.array([s[0]/1.8e9 for s in delay1])
delay1 = np.array([s[0] for s in delay1])
# np.save(path+r'\rt_norm_X',X)
# plt.imshow(X, aspect='auto',extent=[time[0], time[-1], delay[-1], delay[0]], cmap = 'jet')
# plt.show()
gr = X_gr[0]
sat = X_sat[-1]

plt.plot(sat,label = 'sat')
plt.plot(X[10],label = 'state')
plt.plot(gr,label = 'gr')
plt.legend()
plt.show() 

left = 250
right = 280


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


pop = full_pop(time, X, left, right, ground=gr, saturated=sat, order=8)
np.save(r'D:\data_2019-March2020\20200223\Analysis_10dBm_high_pulse_with_delay\4000',pop)
# np.save(r'D:\data\20200305\123509_rabi_ssb_long\delay',delay)

# plt.plot(delay/1e-9, pop, 'o-')
# plt.title(path)
plt.plot(delay1, pop, 'o-')
# plt.plot(delay1/1e9-7.20319, pop, 'o-')
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