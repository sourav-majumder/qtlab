from fitter import *
import numpy as np
import matplotlib.pyplot as plt

#def cosponential(t, tau, norm, phase, n2):
#	return np.abs(norm*np.exp(-t/tau) #+ n2*np.cos(2*np.pi*(freq_m-lock_in_freq)*t + phase))

datadir = 'D:\\data\\2018-08-29\\21-49-45_time_ring_10u_tc_16dB_GHz_6dBm_MHz_4gv\\'
freq, time, r,x, y = np.loadtxt(datadir + 'ZIU_oscillator1_freq_set_time_set.dat', unpack=True)
time_npts = 1000
freq_npts = 21
d1=np.array(time[:time_npts])
d2=np.array(r[6*time_npts:7*time_npts])
freq = freq[::time_npts]
time = time[:time_npts]
x = np.split(x, freq_npts)
y = np.split(y, freq_npts)
r = np.split(r, freq_npts)
time = time[588:680]
r = np.array(r)
r = r[:,582:850]
plt.plot(d2)
plt.show()
rf= Fitter(exponential)
mi=rf.fit(d1[586:750],d2[586:750],print_report=True)
gamma_m = 2/(mi.params['tau'].value*2*np.pi)
quality = freq[6]/gamma_m
print freq[6]/1e6, quality
rf.plot()
rf.save_plot(datadir +'plots\\tau=%fus freq=%.6f MHz.png'%(mi.params['tau'].value*1e6/2, freq[6]/1e6))
# for i,data in enumerate(r):
# 	lock_in_freq = freq[i]
# 	mi = rf.fit(time, data)#tau=200e-6, norm=0.8, phase=0, n2=0.1)
# 	gamma_m = 2/(mi.params['tau'].value*2*np.pi)
# 	quality = freq[i]/gamma_m
# 	print freq[i]/1e6, quality
# 	rf.save_plot(datadir +'plots\\tau=%fus freq=%.6f MHz.png'%(mi.params['tau'].value*1e6/2, freq[i]/1e6))