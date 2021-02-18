import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
from glob import glob

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


path  = r'D:\data\20191009\154339_-3.5repeat2+amp'
path1 = glob(path+'\*red*')
path2 = glob(path+'\*blue*')
path3 = glob(path+'\*peak_curr**')


# wm = 6.583815*1e6
wm = 6.584205*1e6

freq1, psd1 = np.loadtxt(path1[0], unpack = True)
freq2, psd2 = np.loadtxt(path2[0], unpack = True)
peak, curr = np.loadtxt(path3[0], unpack = True)

baseline1 =np.mean(psd1)
baseline2 =np.mean(psd2)

count1=0
count2=0
b1=0
b2=0

for pd1,pd2 in zip(psd1,psd2):
	if pd1 < baseline1 :
		b1=b1+pd1
		count1=count1+1
	if pd2 < baseline2:
		b2 = b2 + pd2
		count2=count2+1

bl1=b1/count1
bl2=b2/count2
cen1=np.argmax(psd1)
cen2=np.argmax(psd2)



area1=np.sum(psd1[cen1-50:cen1+50]-bl1)
area2=np.sum(psd1[cen2-50:cen2+50]-bl1)

# area1 = np.sum(pd - baseline)
# area2 = np.sum(p - baseline) * 200./501
	
area_nor1=area1*(200/501)
area_nor2=area2*(200/501)
area= area_nor1 + area_nor2

print(area,area_nor1,area_nor2,baseline1,baseline2)

fig = plt.figure(figsize = (10,7))

f1 = fig.add_subplot(2,2,1)
plt.plot(curr)
plt.xlabel('counter')
plt.ylabel('current (mA)')

f2 = fig.add_subplot(2,2,2)
plt.plot(peak)
plt.xlabel('counter')
plt.ylabel('cavity peak @ dBm')


f3 = fig.add_subplot(2,1,2)
plt.plot(freq1 - wm, psd1, '-r')
plt.plot(wm - freq2, psd2, '-b')
plt.xlabel('freq')
plt.ylabel('psd (fW)')
plt.grid()
plt.title('A = '+str(area)+ 'A1 = '+str(area_nor1)+ 'A2 = '+str(area_nor2))


plt.tight_layout()
plt.show()


#
#
#def xw(f, f0, k, amp, base):
#	return base + amp* 1./(1. + (2*(f-f0)/k)**2 )
#def xw2(f, f0_1,f0_2, k1, k2 , amp1, amp2, base):
#	return base + amp1* 1./(1. + (2*(f-f0_1)/k1)**2 )+ amp2* 1./(1. + (2*(f-f0_2)/k2)**2 )
#
#
#m = Model(xw2)
#xf = f[130:-100]
#yf = pw_mw_avg[130:-100]
#
##results = m.fit(yf, f = xf, f0 = xf[np.argmax(yf)], k = 6.2, amp = 1, base = 0.4)
#
#results = m.fit(yf, f = xf, f0_1 = xf[np.argmax(yf)], f0_2 = xf[np.argmax(yf)]-8, k1 = 5, k2=8 , amp1 = 1, amp2=0.4, base = 0.5)
#
#f0 = plt.figure(figsize = (10, 4))
#
#f1 = f0.add_subplot(1,2,1)
#plt.plot(xf, yf, '-ro', xf, results.best_fit, '-g', markersize = 3)
#plt.xlabel('Frequency (Hz)')
#plt.ylabel('PSD (fW)')
#plt.title(r'$\gamma_m$ = '+str(results.best_values['k1']))
#
#
#f2 = f0.add_subplot(1,2,2)
#plt.plot(f, 10*np.log10(pw_mw_avg), '-r')
#plt.xlabel('Frequency (Hz)')
#plt.ylabel('PSD (dBm)')
#plt.grid()
#plt.title(' A = '+str(results.best_values['amp1']))
#plt.show()