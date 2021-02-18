import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

powers = list(np.arange(8.3, 8.71, 0.01))
powers.append(8.75)

for power in powers:
	# print r"D:\data Summary\Tanmoy\Time domain at different Power\RefCurve_pw-"+"%.2f"%power+".Wfm.csv"
	ch1, ch2 = np.loadtxt(r"D:\data Summary\Tanmoy\Time domain at different Power\RefCurve_pw-"+"%.2f"%power+".Wfm.csv",
						delimiter=';', unpack=True)

	# ch1 = np.array_split(ch1, 2000)
	# ch2 = np.array_split(ch2, 2000)
	# time = np.linspace(-6.08e-005, 5e-006, len(ch1[0]))

	# plt.scatter(ch1, ch2, marker='.', alpha=0.1)#, 'b.', markerfacecolor=(1, 1, 0, 0.1))
	# plt.show()

	# plt.hist2d(ch1, ch2, bins=40, norm=LogNorm())
	# hist, _, _ = np.histogram2d(ch1, ch2, bins=40)
	# plt.imshow(hist)
	# plt.colorbar()
	# plt.xlim(-4,4)
	# plt.ylim(-4,4)
	# plt.savefig(r"D:\data Summary\Tanmoy\Time domain at different Power\pw-"+"%.2f"%power+".png")
	# plt.close()
	# plt.show()

	# plt.plot(time, ch1[0])
	# plt.plot(time, ch2[0])
	# plt.show()