import numpy as np
from glob import glob


path = r'D:\data\20191018\*200_traces'
#data_name = path+path[16:]+r'.dat'
data_name=glob(path+r'\\*200_traces.dat')

for file in data_name:

    _, fr, pw_dBm1  = np.loadtxt(file, unpack=True, skiprows = 18)
    
    n=200
    
    pw_mw1 = []
    for val in pw_dBm1:
        pw_mw1 = np.append(pw_mw1, 10.**(val/10.))
        
        
    freq = np.split(fr, n)
    # pw_dBm_s = np.array_split(pw_dBm,n)
    pw_mw_s1 = np.split(pw_mw1,n)
    
    pw_mw_avg1 = sum(pw_mw_s1)/n
    f1 = (freq[0])
    pw_mw_avg1 = pw_mw_avg1*1e12
        
    file = open(file[:-4]+'_lin_avg_red.txt', 'w+')
    for index, val in enumerate(f1):
    	file.write(str(val)+'\t'+str(pw_mw_avg1[index])+'\n')
    
    file.close()


#pw_mw2 = []
#for val in pw_dBm2:
#    pw_mw2 = np.append(pw_mw2, 10.**(val/10.))
#
#
#pw_mw_s2 = np.split(pw_mw2,n)
#
#
#pw_mw_avg2 = sum(pw_mw_s2)/n
#f2 = freq[0]
#pw_mw_avg2 = pw_mw_avg2*1e12
#
#file = open(data_name[:-4]+'_lin_avg_blue.dat', 'w+')
#for index, val in enumerate(f2):
#	file.write(str(val)+'\t'+str(pw_mw_avg2[index])+'\n')
#
#file.close()




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