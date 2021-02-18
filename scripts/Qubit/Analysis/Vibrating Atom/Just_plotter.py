import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
from glob import glob

path = r'D:\data\20191017'
#data_name = path+path[16:]+r'.dat'
data_name=glob(path+r'\\142443_-11.0_30_Volt_thermal_motion_amplification**')



for file in data_name:
    path1 = glob(file+r'\*red.dat*')
    path2 = glob(file+r'\*blue.dat*')
    path3 = glob(file+r'\*peak_curr**')
    
    
    freq1, psd1 = np.loadtxt(path1[0], unpack = True)
    freq2, psd2 = np.loadtxt(path2[0], unpack = True)
    peak, curr = np.loadtxt(path3[0], unpack = True)
    
    
    fig = plt.figure(figsize = (10,7))
    
    f1 = fig.add_subplot(2,2,1)
    plt.plot(curr)
    
    f2 = fig.add_subplot(2,2,2)
    plt.plot(peak)
    
    #f3 = fig.add_subplot(2,1,2)
    #plt.plot(freq1, psd1, '-r')
    #plt.plot(freq2, psd2, '-b')
    #plt.grid()
    
    #plt.show()
    
    
    #
    #
    def xw(f, f0, k, amp, base):
    	return base + amp* 1./(1. + (2*(f-f0)/k)**2 )
    #def xw2(f, f0_1,f0_2, k1, k2 , amp1, amp2, base):
    #	return base + amp1* 1./(1. + (2*(f-f0_1)/k1)**2 )+ amp2* 1./(1. + (2*(f-f0_2)/k2)**2 )
    #
    crop_p=1
    m1 = Model(xw)
    xf1 = freq1[crop_p:-crop_p]
    yf1 = psd1[crop_p:-crop_p]
    m2 = Model(xw)
    xf2 = freq2[crop_p:-crop_p]
    yf2 = psd2[crop_p:-crop_p]
#    xf1 = freq1[:-250]
#    yf1 = psd1[:-250]
#    m2 = Model(xw)
#    xf2 = freq2[250:]
#    yf2 = psd2[250:]
    
    #
    results1 = m1.fit(yf1, f = xf1, f0 = xf1[np.argmax(yf1)], k = 6.2, amp = 10, base = 1)
    results2 = m2.fit(yf2, f = xf2, f0 = xf2[np.argmax(yf2)], k = 10, amp = 10, base = 1)
    #
    #results = m.fit(yf, f = xf, f0_1 = xf[np.argmax(yf)], f0_2 = xf[np.argmax(yf)]-8, k1 = 5, k2=8 , amp1 = 1, amp2=0.4, base = 0.5)
    #
    #f0 = plt.figure(figsize = (10, 4))
    
    f3 = fig.add_subplot(2,1,2)
    plt.plot(xf1, yf1, '-ro', xf1, results1.best_fit, '-g', markersize = 3)
    plt.plot(xf2, yf2, '-bo', xf2, results2.best_fit, '-g', markersize = 3)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('PSD (fW)')
    area1=results1.best_values['k']*results1.best_values['amp']/4
    area2=results2.best_values['k']*results2.best_values['amp']/4
    area=area1+area2
    plt.title('curr='+str(file[31:-12])+'0mA  '+'  A = '+str(area)+ 'A1 = '+str(area1)+ 'A2 = '+str(area2))
    #
    #
    #f2 = f0.add_subplot(1,2,2)
    #plt.plot(f, 10*np.log10(pw_mw_avg), '-r')
    #plt.xlabel('Frequency (Hz)')
    #plt.ylabel('PSD (dBm)')
    #plt.grid()
    #plt.title(' A = '+str(results.best_values['amp1']))
    plt.show()