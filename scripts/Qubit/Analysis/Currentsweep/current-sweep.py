import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import gca
import matplotlib as mb


path = r'D:\data\20200213\100602_awg_sweep'

data_name = path+path[16:]+r'.dat'
data = np.loadtxt(data_name, unpack=True)

n = 701
# print(len(data[0]))
# print(len(data[0])/601.0)
curr = np.array_split(data[0],n)
freq = np.array_split(data[1],n)[0]
absol = np.array_split(data[2],n)

# plt.plot(freq, absol[37])
# plt.plot(freq, absol[-1])

fig, ax = plt.subplots()
# fig.title(path[8:])
img = ax.imshow(np.rot90(absol), aspect='auto',extent=[curr[0][0]/1e-3, curr[-1][0]/1e-3, freq[0]/1e9, freq[-1]/1e9], cmap = 'RdBu')
ax.set_xlabel(r'AWG Voltage (mV)')#, fontsize=24)
ax.set_ylabel('Frequency (GHz)')#, fontsize=18)
# ticks_font = mb.font_manager.FontProperties(family='times new roman', style='normal', size=18, weight='normal', stretch='normal')

# for label in ax.get_xticklabels():
#     label.set_fontproperties(ticks_font)

# for label in ax.get_yticklabels():
#     label.set_fontproperties(ticks_font)
fig.colorbar(img, ax=ax)
plt.title(path[8:])
plt.show()

# print(data_name)





