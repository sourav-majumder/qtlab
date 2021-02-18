import numpy as np
from fitter import *
pi = np.pi
data = (r'D:\data\20201212\124847_f0-6dB')

d = Data(data+data[16:]+'.dat', unpack = True)
freq = d.x

c=250

freq = freq[c:-1*c]
s11 = np.abs(d.data)
s11 = s11[c:-1*c]
# data = np.loadtxt(r'C:\Users \Measure\Desktop\ke_cal_0.5mm_depth_perfect_geo.txt', unpack = True)
# freq_arr = data[0]*1e9
# freq = freq_arr
# s11 = data[1]
print(d)
# f = Fitter (S11r)

f = Fitter(rootLorentzianWithOffset)
f.fit(freq, s11, print_report = True)
f.plot()

