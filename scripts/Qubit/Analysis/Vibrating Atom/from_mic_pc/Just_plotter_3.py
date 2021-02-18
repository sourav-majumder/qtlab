import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
from glob import glob


path = r'D:\data\20191011'
#data_name = path+path[16:]+r'.dat'
data_name=glob(path+r'\\*temperature_sweep_25')

for file in data_name:

    path1 = glob(path+'\*red*')
    path2 = glob(path+'\*blue*')
    path3 = glob(path+'\*peak_curr**')
    
    
    # wm = 6.583815*1e6
    #wm = 6.584205*1e6
    wm= 6.582210*1e6
    
    freq1, psd1 = np.loadtxt(path1[0], unpack = True)
    freq2, psd2 = np.loadtxt(path2[0], unpack = True)
    peak, curr = np.loadtxt(path3[0], unpack = True)
    
    
    cen1=np.argmax(psd1)
    cen2=np.argmax(psd2)
    
    
    bl1 =(np.mean(psd1[:cen1-50])+np.mean(psd1[cen1+50:]))/2
    bl2 =(np.mean(psd2[:cen2-50])+np.mean(psd1[cen2+50:]))/2
    
    
    
    area1=np.sum(psd1[cen1-50:cen1+50]-bl1)
    area2=np.sum(psd1[cen2-50:cen2+50]-bl1)
    
    # area1 = np.sum(pd - baseline)
    # area2 = np.sum(p - baseline) * 200./501
    	
    area_nor1=area1*(200/401)
    area_nor2=area2*(200/401)
    area= area_nor1 + area_nor2
    
    print(area,area_nor1,area_nor2,bl1,bl2)
    
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