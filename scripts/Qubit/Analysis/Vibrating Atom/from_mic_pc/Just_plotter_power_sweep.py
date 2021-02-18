import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
from glob import glob

path  = r'D:\data\20191008\*\*_lin_avg.dat'

files = glob(path)

wm = 6.583815*1e6

for file in files:
    plt.figure(figsize = (5, 4))
    freq1, psd1 = np.loadtxt(file, unpack = True)
    baseline = np.mean(psd1[:100])
    area1 = np.sum(psd1 - baseline) * 200./501
    plt.plot(freq1 - wm, psd1, '-r')
    plt.xlabel('freq')
    plt.ylabel('psd (fW)')
    plt.grid()
    plt.title('A = '+str(area1))
    plt.tight_layout()
    plt.savefig(file[:-23]+file[36:-12]+'.png')
    plt.clf()
    



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