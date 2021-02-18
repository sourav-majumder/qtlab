import numpy as np
import matplotlib.pyplot as plt


def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

path = r'D:\data\20190320\200420_omit_5to6_good'
data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)


n = 1
# power= np.array_split(data[0],n)
freq = data[6]
absol = data[4]
# print(freq)


# print(cavity_freq[0])
# plt.plot(cavity_freq[0])
# plt.show()
# print(len(absol[0]))
# absol=np.delete(absol,[133],1)
# print(len(absol[0]))

plt.plot((freq-np.ones(len(freq))*4.52142*1e9)/1e6, 20*np.log10(absol))
plt.xlabel('Detuned sideband (MHz)')
plt.ylabel(r'$S_{21}$ dBm')
plt.show()