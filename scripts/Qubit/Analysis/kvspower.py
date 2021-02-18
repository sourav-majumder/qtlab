import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt

path = r'D:\data\20190826\180629_power_sweep_at_max_sloope_c.038 Cavity_1\180629_power_sweep_at_max_sloope_c.038 Cavity_1.dat'
power, fr, _, _, a ,_ = np.loadtxt(path, unpack=True)

pw = np.linspace(power[0],power[-1],31)
freq = np.split(fr, 31)[0]

data = np.split(a,31)


def S21(f, f0, k, norm):
	return np.abs(norm/(-1j*(f-f0)*(2/k)+1 ))


m = Model(S21)

k_list = []

for i in np.arange(31):
	fguess = freq[np.argmax(data[i])]
	kguess = 6.5e6
	norm_guess = np.max(data[i])
	print(i)
	data2fit = data[i][75:-60]
	f2fit = freq[75:-60]
	result = m.fit(data2fit, f= f2fit, f0 = fguess, k = kguess, norm = norm_guess)
	plt.plot(f2fit, data2fit,'-ro', f2fit, result.best_fit, '-g')
	plt.title(str(pw[i]-30)+' '+'dBm')
	plt.savefig(r'D:\data\20190826\180629_power_sweep_at_max_sloope_c.038 Cavity_1\figs\%f.png'%i, transparent = True)
	plt.clf()
	print(result.best_values['k'])
	k_list = np.append(k_list, result.best_values['k'])


plt.clf()
plt.plot(pw-30, k_list, '-ro')
plt.grid()
plt.show()





# plt.show()

