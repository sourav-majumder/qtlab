import numpy as np
import matplotlib.pyplot as plt
from fitter import *
freq_data, amp_data = np.loadtxt(r'D:\data\20180825\lockin sweeps\meas_sweep_20180829_222653_time_domain_4vplt_6dBmatMHz.txt',skiprows=7,usecols=(0,1),unpack=True)
freq = freq_data[:201]
amp = amp_data[:201]
#plt.plot(freq[:200],amp[:200],freq[200:400],amp[200:400])
#plt.show()
model = Fitter(rootLorentzianWithOffset)
myfit = model.fit(freq,amp,print_report=True)
model.plot()