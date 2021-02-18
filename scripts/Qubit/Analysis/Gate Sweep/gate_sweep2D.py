import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import gca
import matplotlib as mb

path = r'D:\data\20190825\001350_test1'

data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)

n=121

# gate= np.array_split(data[0],n)
freq = np.array_split(data[0],n)[0]
# real = np.array_split(data[2],n)
absol = np.array_split(data[3],n)
print(freq)


plt.title(path[8:])
for i in range(n):
	plt.plot(freq[i]/1e6,absol[i], label= 'Probe -62 dBm')
# plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, power[-1][0], power[0][0]], cmap = 'jet')
plt.xlabel('Drive Frequency (MHz)')
plt.ylabel(r'$S_{21}$')
plt.legend()
plt.show()