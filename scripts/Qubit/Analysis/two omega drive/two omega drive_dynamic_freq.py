import numpy as np
import matplotlib.pyplot as plt
GHz = 1e9

path = r'D:\data\20190307\193346_detuned_2w_drive-2dbm_probe_power_4.66mA'

data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)

pump_freq= np.array_split(data[0],111)
freq = np.array_split(data[1],111)[0]
absol = np.array_split(data[4],111)

# plt.plot(freq, absol[0])
# plt.plot(freq, absol[-1])
plt.title(path[8:])
plt.imshow(np.rot90(absol), aspect='auto',extent=[(pump_freq[0][0]-2*7.414667*GHz)/1e6, (pump_freq[-1][0]-2*7.414667*GHz)/1e6, freq[0]/1e9, freq[-1]/1e9], cmap = 'jet')
plt.xlabel(r'Pump frequency detuned from 2$w_{c}$(MHz)')
plt.ylabel('Frequency (GHz)')
plt.colorbar()
plt.show()







