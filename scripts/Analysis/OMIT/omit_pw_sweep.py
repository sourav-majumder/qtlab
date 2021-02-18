import numpy as np
import matplotlib.pyplot as plt 
from fitter import *

pth = 'D:\\data\\2018-09-08\\14-49-52_omit_pump_pw_sw_mode2\\'

powers, freq, mag, phase = np.loadtxt(pth+'SMF_power_set_S21_frequency_set.dat', unpack=True)

powers = powers[::1001]
freq = freq[:1001]
mag = np.array_split(mag, 11)
phase = np.array_split(phase, 11)

#plt.plot(freq,mag[0])
#plt.show()

omit = Fitter(omit_transmission)

result = []
gamma_m = []

f = open(pth+'gamma_vs_pw.dat','w')


# res = omit.fit(freq,mag[0],print_report=True,gamma = 200.)
# omit.plot()
# ka = res.params['gamma'].value
# print(ka)

for idx, pw in enumerate(powers):
	res = omit.fit(freq,mag[idx],complex_fit=False,print_report=True, gamma = 330)
	#omit.plot()
	ka = res.params['gamma'].value
	Coop = res.params['Cp'].value
	gamma_m.append(ka)
	f.write("%s\t" % pw)
	f.write("%s\t" % Coop)
	f.write("%s\n" % ka)
	omit.save_plot(pth+'fits\\' + str(pw) + '.png')

f.close()

plt.plot(powers,gamma_m,'ro')
print(powers)
print(gamma_m)
