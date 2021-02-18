import numpy as np
from fitter import *
import matplotlib.pyplot as plt
# pi = np.pi
# data = (r'D:\data\20201127\172830_SiN_new_amp1')

# d = Data(data+data[16:]+'.dat', unpack = True)
# freq = d.x
# s11 = np.abs(d.data)
# # data = np.loadtxt(r'C:\Users \Measure\Desktop\ke_cal_0.5mm_depth_perfect_geo.txt', unpack = True)
# # freq_arr = data[0]*1e9
# # freq = freq_arr
# # s11 = data[1]
# # print(d)
# f = Fitter (S11r)
# result=f.fit(freq, s11, print_report = True)
# f.plot()
# print(result.params['ke'].value)
data = np.loadtxt(r'D:\data\20201127\172830_SiN_new_amp1\172830_SiN_new_amp1.dat', unpack = True)
# print(data[1])
plt.plot(data[1],data[2])
plt.show()
