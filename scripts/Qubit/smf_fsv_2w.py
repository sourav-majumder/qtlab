import numpy as np
import matplotlib.pyplot as plt
import qt

from constants import *

def get_power():
	_ , power = fsv.get_max_freqs(1)
	return power[0]

def generate_meta_file():
    metafile = open('D:\\data\\20180118\\low_power_with_smf_and_sa.meta.txt', 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (num_points, start_freq, stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop (unused)\n1\n0\n1\nNothing\n')
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    # metafile.write('#for each of the values\n')
    # values = data.get_values()
    # i=0
    # while i<len(values):
    #     metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
    #     i+=1
    metafile.close()

start_freq = 7.3286e9
stop_freq = 7.36656e9
num_points = 601
freq_array = np.linspace(start_freq, stop_freq, num_points)

fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)

# fsv.set_centerfrequency((7.3286e9+7.36656e9)/2)
# fsv.set_span(7.36656e9-7.3286e9)
# fsv.set_bandwidth(1*kHz)
# fsv.set_sweep_points(601)

# fh = open('D:\\data\\20180118\\low_power_with_smf_and_sa.txt', 'a')
# fig, ax = plt.subplots()
# ax.plot([1,2], [1,2])
# fig.canvas.draw()

inst = fsv.get_instrument()

values = []

for freq in freq_array:
	smf.set_frequency(freq)
	fsv.set_centerfrequency(freq)
	qt.msleep(1)
	fsv.marker_to_max()
	inst.write('CALC:MARK:X %.10e'%freq)
	value = get_power()
	values.append(value)
	# print '%.10e %.10e\n'%(freq, value)
	# fh.write('%.10e %.10e\n'%(freq, value))

	# ax.clear()
	# ax.plot(freq_array[:len(values)], values)
	# fig.canvas.draw()
	# generate_meta_file()

values = np.array(values)
np.savetxt('D:\\data\\20180118\\low_power_with_smf_and_sa.values', values)
np.savetxt('D:\\data\\20180118\\low_power_with_smf_and_sa.freq', freq_array)
plt.plot(freq_array, values)
plt.show()
# fh.close()