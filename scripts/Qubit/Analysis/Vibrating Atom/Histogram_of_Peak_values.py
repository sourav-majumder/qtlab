# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 18:12:55 2019

@author: Measure
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
from glob import glob

path  = r'D:\data\20191010'



files = glob(path+r'\\*red_alone\\*_peak*')

f = plt.figure(figsize = (9,4))

giant_peak =[]

for file in files:
    filetoken = file[50:-40]
    peak, _ = np.loadtxt(file, unpack = True)
    giant_peak = np.concatenate(giant_peak, peak)

cut = giant_peak.reshape(5,800)

for i in np.arange(5):
    plt.hist(cut[i], bins = 25, alpha = 0.5)

plt.show()

#plt.savefig(path+r'\\Histogram analysis of peak\\'+filetoken+'_t.png', transparent = True)