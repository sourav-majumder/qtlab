import numpy as np
import matplotlib.pyplot as plt

def find_jump(data, min_r, phase_threshold):
	phase_diff = np.abs(np.angle(data[0])-np.angle(data[-1]))
	if phase_diff > np.pi:
		phase_diff -= 2*np.pi
		phase_diff = np.abs(phase_diff)
	if np.abs(data[0]) > min_r and np.abs(data[-1]) > min_r and phase_diff > phase_threshold:
		# plt.plot([np.real(data[0]),np.real(data[-1])], [np.imag(data[0]),np.imag(data[-1])], 'r')
		# print '|%f| exp( %f )\t|%f| exp( %f ) YES %f'%(np.abs(data[0]), np.angle(data[0]), np.abs(data[-1]), np.angle(data[-1]), phase_diff)
		return 1
	else:
		# print '| %f| exp( %f )\t|%f| exp( %f ) NO'%(np.abs(data[0]), np.angle(data[0]), np.abs(data[-1]), np.angle(data[-1]))
		return 0

def find_jumps(data, bin_no, min_r, phase_threshold):
	jumps = []
	for i in range(len(data)/bin_no):
		jumps.append(find_jump(data[(i*bin_no):(i*bin_no)+bin_no], min_r, phase_threshold))
	return np.array(jumps)

powers = list(np.arange(8.3, 8.71, 0.01))
powers.append(8.75)

datafile = open("jump_data.dat", "w")
datafile.write("#POWER vs JUMPS vs TIME\n")

for power in powers:
	print power
	ch1, ch2 = np.loadtxt(r"D:\data Summary\Tanmoy\Time domain at different Power\RefCurve_pw-"+"%.2f"%power+".Wfm.csv",
							delimiter=';', unpack=True)

	full_data = ch1 + 1j*ch2
	full_data = np.array_split(full_data, 2000)
	bin_no = 30

	jumps = np.zeros(len(full_data[0])/bin_no)
	for data in full_data:
		jumps += find_jumps(data, bin_no, 1, 0.4)

	datafile.write("#POWER : %.2f\n"%power)
	for val in jumps:
		datafile.write("%d\t"%val)
	datafile.write("\n")

datafile.close()
# plt.plot(jumps)
# plt.show()