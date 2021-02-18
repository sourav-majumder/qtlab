import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import gca
import matplotlib as mb

path = r'D:\data\20190825\073948_test2'

data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)

n=82

gate= np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]
real = np.array_split(data[2],n)
absol = np.array_split(data[4],n)
print(freq)


plt.title(path[8:])
plt.imshow(absol, aspect='auto',extent=[freq[0]/1e6, freq[-1]/1e6, gate[-1][0], gate[0][0]], cmap = 'RdBu')
plt.xlabel('Drive Frequency (MHz)')
plt.ylabel(r'Gate voltage (V)')
plt.colorbar()
plt.show()

	
## incomplte code
## Target of this code was to get a frequency plot for zero crossing fro different gate voltage

