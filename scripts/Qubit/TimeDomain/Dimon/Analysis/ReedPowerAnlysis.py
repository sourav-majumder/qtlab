import numpy as np
import matplotlib.pyplot as plt

path = r'D:\data\20201228\190937_cavity_bare_freq_without_pi_bright'
data_name = path+path[16:]+r'.dat'
data_bare = np.loadtxt(data_name, unpack=True)


freq_bare = data_bare[0][0]
power_bare = data_bare[1]
absol_bare = data_bare[2]


path = r'D:\data\20201228\190527_cavity_bare_freq_with_pi_bright'
data_name = path+path[16:]+r'.dat'
data_pi = np.loadtxt(data_name, unpack=True)



absol_pi = data_pi[2]



# print(pow_arr)
# plt.plot(freq, absol[-1])
# plt.title(path[8:])
plt.plot(power_bare, 20*np.log10(np.array(absol_pi)), 'b.', label = 'pi')
plt.plot(power_bare, 20*np.log10(np.array(absol_bare)), 'r.', label = 'bare')
plt.xlabel('Power (dBm)')
plt.ylabel('Voltage')
plt.legend()
# plt.colorbar()
plt.show()







