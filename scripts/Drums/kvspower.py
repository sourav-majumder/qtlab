import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt

path = r'D:\data\20191206\141911_power_sweep_evaporated_drum_device\141911_power_sweep_evaporated_drum_device.dat'
power, fr, _, _, a ,_ = np.loadtxt(path, unpack=True)

pw = np.linspace(power[10],power[-60],71)
freq = np.split(fr, 71)[0]

data = np.split(a,71)


def normalizedS11(f, f0, ke, ki):
	return 1-ke/((ki+ke)/2+1j*(f-f0))

def S11(f, f0, ke, ki, norm):
	return norm*normalizedS11(f, f0, ke, ki)

def S11r(f, f0, ke, ki, norm):
	return norm*np.abs(normalizedS11(f, f0, ke, ki))

m = Model(S11r)

k_list = []
ke_list= []
for i in np.arange(70):
	fguess = freq[np.argmin(data[i])]
	keguess = 1e5
	kiguess = 1e5
	norm_guess = np.min(data[i])
	# # print(i)
	data2fit = data[i]
	f2fit = freq
	result = m.fit(data2fit, f= f2fit, f0 = fguess, ke = keguess, ki = kiguess, norm = norm_guess)
	plt.plot(f2fit, data2fit,'-ro', f2fit, result.best_fit, '-g')
	plt.title(str(pw[i])+' '+'dBm')
	plt.savefig(r'D:\data\20191206\141911_power_sweep_evaporated_drum_device\figs\%f.png'%i, transparent = True)
	plt.clf()
	# print(result.params['ke'].value)
	k_list = np.append(k_list, (pw[i], result.params['ke'].value, result.params['ki'].value))
	ke_list= np.append(ke_list, result.params['ki'].value)
with open('list.txt', 'w') as f:
    for item in k_list:
        f.write("%s\n" % item)
print(len(pw))
# plt.clf()
plt.plot(pw[:70], ke_list, '-ro')
plt.grid()
plt.show()

