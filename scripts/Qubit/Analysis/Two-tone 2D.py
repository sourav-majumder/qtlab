import numpy as np
import matplotlib.pyplot as plt


def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

path = r'D:\data\20190318\232524_Qubit qfreq_as_current_lower_drive5dBm'

data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)


n = 5
power= np.array_split(data[0],n)
freq = np.array_split(data[1],n)
absol = np.array_split(data[4],n)
# print(len(absol[0]))
# absol=np.delete(absol,[133],1)
# print(len(absol[0]))
plt.title(data_name)
for i in range(n):
	plt.plot(freq[i]/1e9,absol[i], label= '{} mA'.format(power[i][0]/1e-3))
# plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, power[-1][0], power[0][0]], cmap = 'jet')
plt.xlabel('Drive Frequency (GHz)')
plt.ylabel(r'$S_{21}$')
plt.legend()
plt.show()