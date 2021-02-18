# central_freq = 6.72e6
# cavity_freq = 6.025e9
# span = 10e3
# off_freq = 8072
# points = 5001

# freq = central_freq - span/2 + off_freq + cavity_freq
# print(freq/1e9)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import gca
import matplotlib as mb


path = r'D:\data\20191104\190209_thermal_peak_detection100avg'

data_name = path+path[16:]+r'.dat'
freq = np.loadtxt(data_name, unpack=True)[1]
peak = np.loadtxt(data_name, unpack=True)[2]
result = np.where(peak>=-116.5)
result = np.array(result[0])
p = np.zeros(len(result))
for idx, i in enumerate(result):
	p[idx] = freq[i]

# np.save(path+r'\peak',p)
print(len(p))

