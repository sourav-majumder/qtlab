import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


data = np.loadtxt('D:\\data\\20200328\\test.Wfm.csv', delimiter = ';', usecols = (0,1), unpack = True)
header = pd.read_csv('D:\\data\\20200328\\test.csv')

# header = np.loadtxt('D:\\data\\20200328\\test.csv', delimiter = ':', usecols = (0), unpack = True)

start = float(header['CPgReferenceCurveAttributes:SourceType:Source:'][11][7:-1])
stop = float(header['CPgReferenceCurveAttributes:SourceType:Source:'][12][6:-1])
length = float(header['CPgReferenceCurveAttributes:SourceType:Source:'][13][19:-1])
print(start, stop,length)
# np.loadtxt('D:\\data\\20200328\\test.csv', delimiter = ':')