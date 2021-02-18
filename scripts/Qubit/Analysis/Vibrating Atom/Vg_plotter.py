# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 18:12:55 2019

@author: Measure
"""

import numpy as np
import matplotlib.pyplot as plt

path=r'D:\data\20191013\233818_DC_SWEEP_-30TO+30'
filename=path.split('\\')[-1]+'.dat'
data = np.loadtxt(path+'\\'+filename, unpack = True)
ax0 = np.unique(data[0])
ax1 = np.unique(data[1])
data_dg=np.split(data[0],301)
data_r=np.split(data[1],301)

giant_list = []
idx = 0

for idx0, val0 in enumerate(ax0):
    for idx1, val1 in enumerate(ax1):
        if val1 in data_r[idx0]:
            giant_list = np.append(giant_list, data[2][idx])
            idx=idx+1
        else:
            giant_list = np.append(giant_list, 0.0)
    print(idx)


asp = (np.abs(ax0[0]-ax0[-1]))/(np.abs(ax1[0]-ax1[-1]))
ext = [ax1[0], ax1[-1], ax0[0], ax0[-1]]
giant_list_2D=giant_list.reshape(len(ax0), len(ax1))
plt.imshow(giant_list_2D, extent = ext, aspect = 1/asp)
plt.show()
    