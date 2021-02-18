import numpy as np
import matplotlib.pyplot as plt


def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

path = r'D:\data\20200129\111213_lzs_freq'

data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)


n = 10
power= np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]
absol = np.array_split(data[4],n)
# print(len(absol[0]))
# absol=np.delete(absol,[133],1)
# print(len(absol[0]))
plt.title(path[8:])
plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, power[-1][0]/1e6, power[0][0]/1e6], cmap = 'RdBu', label='Drive 0dBm')
plt.xlabel('Drive Frequency (GHz)')
plt.ylabel(r'AWG oscillation Frequency (MHz)')
plt.colorbar()
plt.show()

#