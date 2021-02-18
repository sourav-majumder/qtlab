import numpy as np
import matplotlib.pyplot as plt


def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

path = r'D:\data\20190318\232524_Qubit qfreq_as_current_lower_drive5dBm'
cavity_path = r'D:\data\20190318\232524_cavity qfreq_as_current_lower_drive5dBm'

data_name = path+path[16:]+r'.dat'
cavity_data_name = cavity_path+cavity_path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)
cavity_data = np.loadtxt(cavity_data_name, unpack=True)


n = 5
power= np.array_split(data[0],n)
freq = np.array_split(data[1],n)
absol = np.array_split(data[4],n)

cavity_absol = np.array_split(cavity_data[2],n)
cavity_freq = np.array_split(cavity_data[1],n)

# print(cavity_freq[0])
# plt.plot(cavity_freq[0])
# plt.show()
# print(len(absol[0]))
# absol=np.delete(absol,[133],1)
# print(len(absol[0]))

# plt.figure(1)
fig, ax = plt.subplots(n, sharex=True, sharey=True)
fig.suptitle(path[8:])
for i in range(n):
	# plt.subplot('{}'.format(int(str(n)+'1'+str(i+1))))
	ax[i].plot(freq[i]/1e9,absol[i], label= '{} mA, Probe {:.4} GHz'.format(power[i][0]/1e-3,cavity_freq[i][np.argmax(cavity_absol[i])]/1e9))
	ax[i].legend()
# plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, power[-1][0], power[0][0]], cmap = 'jet')
# plt.xlabel('Drive Frequency (GHz)')
# plt.ylabel(r'$S_{21}$')

fig.text(0.5,0.04, 'Drive frequency (GHz)', ha="center", va="center")
fig.text(0.05,0.5, r'$S_{21}$', ha="center", va="center", rotation=90)
fig.subplots_adjust(hspace=0)
plt.show()