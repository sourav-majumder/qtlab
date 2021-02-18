import numpy as np
from lmfit import Model
import matplotlib.pyplot as plt

#D:\data\20191005\151127_ibias11
#D:\data\20191005\144214_ibias10
#D:\data\20191005\141025_ibias9
#D:\data\20191005\134514_ibias8
#D:\data\20191005\131804_ibias7
#D:\data\20191005\125006_ibias6
#D:\data\20191005\122534_ibias5
#D:\data\20191005\120000_ibias4
#D:\data\20191005\113603_ibias3
#D:\data\20191005\110753_ibias2
#D:\data\20191005\103049_ibias390mA


path = r'D:\data\20191017\120034_-13.0_30_Volt_thermal_motion_amplification'
data_name = path+path[16:]+r'.dat'
_, fr, pw_dBm, _ = np.loadtxt(data_name, unpack=True, skiprows = 22)

pw_mw = []
for val in pw_dBm:
    pw_mw = np.append(pw_mw, 10.**(val/10.))

n=100
freq = np.array_split(fr, n)
pw_dBm_s = np.array_split(pw_dBm,n)
pw_mw_s = np.array_split(pw_mw,n)

pw_dBm_avg = sum(pw_dBm_s)/n
pw_mw_avg = sum(pw_mw_s)/n

pw_mw_avg_dBm = 10*np.log10(pw_mw_avg)


plt.plot(freq[0] - 6018.416185e6 , pw_dBm_avg, '-r')
plt.grid()
plt.xlabel('Frequency (Hz)')
plt.ylabel('PSD (dBm)')
plt.ylim(-125, -114)
plt.tight_layout()
plt.show()

#plt.plot(freq[0], pw_dBm_avg, '-r', freq[0], pw_mw_avg_dBm, '-g')
#plt.show()

#plt.plot(freq[0], pw_mw_avg, '-r')
#plt.show()

#def xw(f, f0, k, amp, base):
#	return base + amp* 1./(1. + (2*(f-f0)/k)**2 )
#
#
#m = Model(xw)
#xf = freq[0][100:-100]
#yf = pw_mw_avg[100:-100]
#
#results = m.fit(yf, f = xf, f0 = xf[np.argmax(yf)], k = 6.2, amp = 4e-12, base = 0.9e-12)
#plt.plot(xf, yf, '-r', xf, results.best_fit, '-g')
#plt.show()