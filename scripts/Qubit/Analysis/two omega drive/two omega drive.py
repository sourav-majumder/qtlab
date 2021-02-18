import numpy as np
import matplotlib.pyplot as plt

data_name = r'D:\data\20190222\115713_two_omega_drive_at qubit_resonance_drive15M_detuned\115713_two_omega_drive_at qubit_resonance_drive15M_detuned.dat'

data = np.loadtxt(data_name, unpack=True)

power= np.array_split(data[0],81)
freq = np.array_split(data[1],81)[0]
absol = np.array_split(data[4],81)

# plt.plot(freq, absol[0])
# plt.plot(freq, absol[-1])
plt.title(data_name)
plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, power[-1][0], power[0][0]], cmap = 'jet')
plt.xlabel('Frequency (GHz)')
plt.ylabel(r'Drive Power at 2$w_{c}$(dBm)')
plt.colorbar()
plt.show()







