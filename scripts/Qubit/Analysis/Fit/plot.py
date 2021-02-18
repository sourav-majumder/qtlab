import matplotlib.pyplot as plt
import numpy as np


P1 = np.loadtxt(r'D:\data\20191108\curr-3.5.txt')
P2 = np.loadtxt(r'D:\data\20191108\curr-3.25.txt')
P3 = np.loadtxt(r'D:\data\20191108\curr-3.1.txt')
P4 = np.loadtxt(r'D:\data\20191108\curr-3.txt')
P5 = np.loadtxt(r'D:\data\20191108\curr-2.9.txt')
P6 = np.loadtxt(r'D:\data\20191108\curr-2.75.txt')
P7 = np.loadtxt(r'D:\data\20191108\curr-2.5.txt')
# P8 = np.loadtxt(r'D:\data\20190802\negative21.5.txt')
# P9 = np.loadtxt(r'D:\data\20190802\negative19.5.txt')

# fig1, ax1 = plt.subplots(nrows=1, ncols=1, sharex=True)
# ax1.errorbar(P1[0], P1[1], fmt='.', yerr = P1[2] ,capsize=2, elinewidth=1, markeredgewidth=2, label = 'position_1')
# ax1.errorbar(P2[0], P2[1], fmt='.', yerr = P2[2] ,capsize=2, elinewidth=1, markeredgewidth=2, label = 'position_2')
# ax1.errorbar(P3[0], P3[1], fmt='.', yerr = P3[2] ,capsize=2, elinewidth=1, markeredgewidth=2, label = 'position_3')
# ax1.errorbar(P4[0], P4[1], fmt='.', yerr = P4[2] ,capsize=2, elinewidth=1, markeredgewidth=2, label = 'position_4')
# ax1.errorbar(P5[0], P5[1], fmt='.', yerr = P5[2] ,capsize=2, elinewidth=1, markeredgewidth=2, label = 'position_5')
# # ax.plot(power.T[0],(f0/ki)/1e3)
# ax1.set_xlabel(r'Photon number')
# ax1.set_ylabel(r'Linewidth (MHz)')
# ax1.set_xscale('log')
# ax1.set_title(path[8:])
fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
ax.errorbar(P1[0], P1[3], fmt='.', yerr = P1[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-3.5mA')
ax.errorbar(P2[0], P2[3], fmt='.', yerr = P2[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-3.25mA')
ax.errorbar(P3[0], P3[3], fmt='.', yerr = P3[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-3.1mA')
ax.errorbar(P4[0], P4[3], fmt='.', yerr = P4[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-3mA')
ax.errorbar(P5[0], P5[3], fmt='.', yerr = P5[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-2.9mA')
ax.errorbar(P6[0], P6[3], fmt='.', yerr = P6[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-2.75mA')
ax.errorbar(P7[0], P7[3], fmt='.', yerr = P7[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-2.5mA')
# ax.errorbar(P8[0], P8[3], fmt='.', yerr = P8[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-21.5mA')
# ax.errorbar(P9[0], P9[3], fmt='.', yerr = P9[4] ,capsize=2, elinewidth=1, markeredgewidth=2, label = '-19.5mA')



# ax.plot(power.T[0],(f0/ki)/1e3)
ax.set_xlabel(r'Photon number')
ax.set_ylabel(r'Q (kU)')
ax.set_xscale('log')

plt.legend()
plt.show()