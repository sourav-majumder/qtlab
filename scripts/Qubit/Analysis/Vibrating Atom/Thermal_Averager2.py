import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt

#D:\data\20191008\131547_-3.5
#D:\data\20191008\133248_-4.0
#D:\data\20191008\134949_-4.5
#D:\data\20191008\140651_-5.0
#D:\data\20191008\142430_-5.5
#D:\data\20191008\144135_-6.0
#D:\data\20191008\145836_-6.5
#D:\data\20191008\151552_-7.0
#D:\data\20191008\153255_-7.5
#D:\data\20191008\155006_-8.0



#D:\data\20191008\161024_-3.5
#D:\data\20191008\162725_-4.0



path = r'D:\data\20191008\133248_-4.0'
data_name = path+path[16:]+r'.dat'
_, fr, pw_dBm, _, _ = np.loadtxt(data_name, unpack=True, skiprows = 22)

n=401

pw_mw = []
for val in pw_dBm:
    pw_mw = np.append(pw_mw, 10.**(val/10.))


freq = np.array_split(fr, n)
# pw_dBm_s = np.array_split(pw_dBm,n)
pw_mw_s = np.array_split(pw_mw,n)


pw_mw_avg = sum(pw_mw_s)/n
f = freq[0] - 6018.416185e6
pw_mw_avg = pw_mw_avg*1e12

print(data_name[:-4]+'_lin_avg.dat')

file = open(data_name[:-4]+'_lin_avg.dat', 'w+')
for index, val in enumerate(f):
	file.write(str(val)+'\t'+str(pw_mw_avg[index])+'\n')

file.close()




# def xw(f, f0, k, amp, base):
# 	return base + amp* 1./(1. + (2*(f-f0)/k)**2 )
# def xw2(f, f0_1,f0_2, k1, k2 , amp1, amp2, base):
# 	return base + amp1* 1./(1. + (2*(f-f0_1)/k1)**2 )+ amp2* 1./(1. + (2*(f-f0_2)/k2)**2 )


# m = Model(xw2)
# xf = f[130:-100]
# yf = pw_mw_avg[130:-100]

# #results = m.fit(yf, f = xf, f0 = xf[np.argmax(yf)], k = 6.2, amp = 1, base = 0.4)

# results = m.fit(yf, f = xf, f0_1 = xf[np.argmax(yf)], f0_2 = xf[np.argmax(yf)]-8, k1 = 5, k2=8 , amp1 = 1, amp2=0.4, base = 0.5)

# f0 = plt.figure(figsize = (10, 4))

# f1 = f0.add_subplot(1,2,1)
# plt.plot(xf, yf, '-ro', xf, results.best_fit, '-g', markersize = 3)
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('PSD (fW)')
# plt.title(r'$\gamma_m$ = '+str(results.best_values['k1']))


# f2 = f0.add_subplot(1,2,2)
# plt.plot(f, 10*np.log10(pw_mw_avg), '-r')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('PSD (dBm)')
# plt.grid()
# plt.title(' A = '+str(results.best_values['amp1']))
# plt.show()