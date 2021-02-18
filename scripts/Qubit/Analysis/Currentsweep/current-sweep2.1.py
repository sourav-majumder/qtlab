import numpy as np
import matplotlib.pyplot as plt


data_name1 = r'D:\data\20200121\110908_curr_sweep2'

# data_name2 = r'D:\data\20190305\163721_curr_sweep\163721_curr_sweep.dat'
# data_name3 = r'D:\data\20190305\171006_curr_sweep\171006_curr_sweep.dat'

data1 = np.loadtxt(data_name1, unpack=True)

curr1= np.array_split(data1[0],151)
freq1 = np.array_split(data1[1],151)[0]
absol1 = np.array_split(data1[2],151)

# data2 = np.loadtxt(data_name2, unpack=True)

# curr2= np.array_split(data2[0],301)
# freq2 = np.array_split(data2[1],301)[0]
# absol2 = np.array_split(data2[2],301)



# absol = np.concatenate((absol1[:151],absol2))
# plt.plot(freq, absol[0])
# plt.plot(freq, absol[-1])
# plt.title(data_name)
plt.imshow(np.rot90(absol1), aspect='auto',extent=[-1.0, 2.0, freq1[0]/1e9, freq1[-1]/1e9], cmap = 'jet')
plt.xlabel('Current(mA)')
plt.ylabel('Frequency (GHz)')
plt.colorbar()
plt.show()







