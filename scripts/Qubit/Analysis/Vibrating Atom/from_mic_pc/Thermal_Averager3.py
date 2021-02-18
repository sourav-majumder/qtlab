import numpy as np

#D:\data\20191008\181117_-3.5repeat
#D:\data\20191008\185607_-3.5repeat
#D:\data\20191008\223148_-3.5repeat
#D:\data\20191008\231628_-3.5repeat



#D:\data\20191009\104246_-6.5repeat2
#D:\data\20191009\113620_-6.5repeat2
#D:\data\20191009\122059_-6.5repeat2

#D:\data\20191009\132557_-6.5repeat2+amp
#D:\data\20191009\135307_-6.5repeat2+amp
#D:\data\20191009\141836_-6.5repeat2+amp

#D:\data\20191009\154339_-3.5repeat2+amp
#D:\data\20191009\161712_-3.5repeat3
#D:\data\20191009\163932_-3.5repeat3
#D:\data\20191009\170205_-3.5repeat3

#D:\data\20191009\175430_-4.5repeat3
#D:\data\20191009\181702_-5.5repeat3
#D:\data\20191009\184032_-6.5repeat3
#D:\data\20191009\190305_-7.5repeat3
#D:\data\20191009\192530_-8.5repeat3
#D:\data\20191009\194840_-9.5repeat3
#D:\data\20191009\201129_-10.5repeat3
#D:\data\20191009\203354_-11.5repeat3
#D:\data\20191009\205618_-12.5repeat3


path = r'D:\data\20191009\205618_-12.5repeat3'
data_name = path+path[16:]+r'.dat'
_, fr, pw_dBm1, pw_dBm2  = np.loadtxt(data_name, unpack=True, skiprows = 22)

n=200

pw_mw1 = []
for val in pw_dBm1:
    pw_mw1 = np.append(pw_mw1, 10.**(val/10.))


freq = np.split(fr, n)
# pw_dBm_s = np.array_split(pw_dBm,n)
pw_mw_s1 = np.split(pw_mw1,n)


pw_mw_avg1 = sum(pw_mw_s1)/n
f1 = np.abs(freq[0])
pw_mw_avg1 = pw_mw_avg1*1e12

file = open(data_name[:-4]+'_lin_avg_red.dat', 'w+')
for index, val in enumerate(f1):
	file.write(str(val)+'\t'+str(pw_mw_avg1[index])+'\n')

file.close()


pw_mw2 = []
for val in pw_dBm2:
    pw_mw2 = np.append(pw_mw2, 10.**(val/10.))


pw_mw_s2 = np.array_split(pw_mw2,n)


pw_mw_avg2 = sum(pw_mw_s2)/n
f2 = freq[0]
pw_mw_avg2 = pw_mw_avg2*1e12

file = open(data_name[:-4]+'_lin_avg_blue.dat', 'w+')
for index, val in enumerate(f2):
	file.write(str(val)+'\t'+str(pw_mw_avg2[index])+'\n')

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