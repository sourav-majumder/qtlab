import numpy as np
import matplotlib.pyplot as plt


def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

path = r'D:\data\20190718\155221_Qubit smart_two_tone2'
cavity_path = r'D:\data\20190718\155221_cavity smart_two_tone2'

data_name = path+path[16:]+r'.dat'
cavity_data_name = cavity_path+cavity_path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)
cavity_data = np.loadtxt(cavity_data_name, unpack=True)


n = 5
power= np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]
absol = np.array_split(data[4],n)

cavity_absol = np.array_split(cavity_data[2],n)
cavity_freq = np.array_split(cavity_data[1],n)
print(cavity_freq[-1][np.argmax(cavity_absol[-1])]/1e9)

plt.title(path[8:])
plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, cavity_freq[-1][np.argmax(cavity_absol[-1])]/1e9, cavity_freq[0][np.argmax(cavity_absol[0])]/1e9], cmap = 'RdBu')
plt.xlabel('Drive Frequency (GHz)')
plt.ylabel(r'Probe Frequency (GHz)')
plt.colorbar()
plt.show()


