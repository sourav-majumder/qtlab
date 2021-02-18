import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt

path = r'D:\data\20210114\001315_high_mag_power_sweep_wc_5.943GHz'
data_name = path+path[16:]+r'.dat'
power, fr, _, _, a ,_ = np.loadtxt(data_name, unpack=True)

n=21

pw = np.linspace(power[0],power[-1],n)
freq = np.split(fr, n)[0]

data = np.split(a,n)

# plt.plot(data[11][80:-40])
# plt.show()


def S21(f, f0, k, norm):
	return np.abs(norm/(-1j*(f-f0)*(2/k)+1 ))


m = Model(S21)

k_list = []
pw_list= []

f1=open(path+'\\power_vs_kappa'+'.txt','w+')

for i in np.arange(n):
	fguess = freq[np.argmax(data[i])]
	kguess = 4.1e6
	norm_guess = np.max(data[i])
	print(i)
	data2fit = data[i][80:-50]
	f2fit = freq[80:-50]
	result = m.fit(data2fit, f= f2fit, f0 = fguess, k = kguess, norm = norm_guess)
	plt.plot(f2fit, data2fit,'-ro', f2fit, result.best_fit, '-g')
	plt.title(str(pw[i]))
	plt.savefig(path+'\\figs\\%d.png'%i, transparent = True)
	plt.clf()
	print(result.best_values['k'])

	f1.write(str(pw[i])+'\t'+str(result.best_values['k'])+'\t'+str(result.best_values['norm'])+'\t'+str(20*np.log10(result.best_values['norm']))+'\n')
	
	k_list = np.append(k_list, result.best_values['k'])
	pw_list= np.append(pw_list, result.best_values['norm'])

f1.close()
plt.clf()
plt.plot(pw, k_list/1e6, '-ro')
plt.xlabel('Input Power(dBm)')
plt.ylabel('Cavity linewidth(MHz)')
plt.grid()
plt.show()

plt.plot(pw,20*np.log10(pw_list),'-bo')

plt.grid()
plt.show()




plt.show()

