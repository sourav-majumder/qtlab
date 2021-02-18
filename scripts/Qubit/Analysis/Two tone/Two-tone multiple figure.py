import numpy as np
import matplotlib.pyplot as plt


def volt(dBm):
	return np.sqrt(50*1e-3*(10**(dBm/10)))

path = r'D:\data\20190321\224709_two_tone_2Dqubit_v2'
data_name = path+path[16:]+r'.dat'

data = np.loadtxt(data_name, unpack=True)


n = 5
power= np.array_split(data[0],n)
freq = np.array_split(data[1],n)
absol = np.array_split(data[4],n)


# print(cavity_freq[0])
# plt.plot(cavity_freq[0])
# plt.show()
# print(len(absol[0]))
# absol=np.delete(absol,[133],1)
# print(len(absol[0]))

# plt.figure(1)
fig, ax = plt.subplots(n, sharex=True)
fig.suptitle(path[8:])
for i in range(n):
	# plt.subplot('{}'.format(int(str(n)+'1'+str(i+1))))
	ax[i].plot(freq[i]/1e9,absol[i], label= '{} dBm'.format(power[i][0]-50))
	ax[i].legend()
	ax[i].axes.yaxis.set_ticklabels([])
# plt.imshow(absol, aspect='auto',extent=[freq[0]/1e9, freq[-1]/1e9, power[-1][0], power[0][0]], cmap = 'jet')
# plt.xlabel('Drive Frequency (GHz)')
# plt.ylabel(r'$S_{21}$')

fig.text(0.5,0.04, 'Drive frequency (GHz)', ha="center", va="center")
fig.text(0.1,0.5, r'$S_{21}$', ha="center", va="center", rotation=90)
fig.subplots_adjust(hspace=0)
plt.show()