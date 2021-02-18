import numpy as np
import matplotlib.pyplot as plt

path = r'D:\data\20200121\154008_Power_Sweep_7.5G_qubit'

data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)

n=71
power = np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]
absol = np.array_split(data[4],n)



# print(pow_arr)
# plt.plot(freq, absol[-1])
plt.title(path[8:])
plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, power[-1][0]-8, power[0][0]-8], cmap = 'RdBu')
plt.xlabel('Frequency (GHz)')
plt.ylabel('Power(dBm)')
# plt.colorbar()
plt.show()







