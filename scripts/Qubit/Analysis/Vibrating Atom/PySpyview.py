# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 12:03:24 2019

@author: Measure
"""

import numpy as np
import matplotlib.pyplot as plt

file_name = r'D:\data\20191011\160303__-30_cavity_-10.0_smf_50mk\160303_-30_cavity_-10.0_smf_50mk.dat'
data = np.loadtxt(file_name, skiprows = 18, unpack= True)

psd = data[2].reshape(50,201)
plt.imshow(psd)
plt.show()