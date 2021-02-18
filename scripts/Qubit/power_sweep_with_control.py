import qt
import numpy as np
import shutil
import sys
import os
from constants import *
import time

# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)

measurement_power_start = 10 # At VNA. 30 dB attenuation after VNA
measurement_power_stop = -60
measurement_power_numpoints = 71
measurement_power_array = np.linspace(measurement_power_start, measurement_power_stop, measurement_power_numpoints)

numpoints = znb.get_numpoints()
freq_array = znb.get_frequency_data()
znb.set_source_power(measurement_power_array[0])

def generate_meta_file(no_of_measurement_power, measurement_power):
	metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
	metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
			(numpoints,  freq_array[0]/GHz, freq_array[-1]/GHz, 'Frequency (GHz))'))
	metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
			(no_of_measurement_power, measurement_power, measurement_power_array[0], 'measurement Power (dBm)'))
	metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

	metafile.write('#for each of the values\n')
	values = data.get_values()
	i=0
	while i<len(values):
		metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
		i+=1
	metafile.close()


def bandwidth(power):
    if power<=-50 and power>=-60:
        return 1
    elif power<=-40 and power>-50:
        return 1
    elif power<=-30 and power>-40:
        return 10
    elif power<=-20 and power>-30:
        return 30
    elif power<=-10 and power>-20:
        return 50
    elif power<=0 and power>-10:
        return 50
    elif power<=10 and power>0:
        return 50


data_file_name = raw_input('Enter name of data file: ')
data=qt.Data(name=data_file_name)
data.add_coordinate('measurement_Power', units='dBm')
data.add_coordinate('Frequency', units='Hz')
data.add_value('S21 Real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')

qt.mstart()

assert raw_input('continue? [y/n]').upper() != 'N'

measurement_power_progress_bar = progressbar.ProgressBar(maxval=measurement_power_numpoints, \
	widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
measurement_power_progress_bar.start()

start = time.time()

for no_of_measurement_power, measurement_power in enumerate(measurement_power_array):
	znb.set_source_power(measurement_power)
	znb.set_if_bandwidth(bandwidth(measurement_power))
	znb.send_trigger(wait=True)
	znb.autoscale()
	traces = []
	trace = znb.get_data('S21')
	traces.append(np.real(trace))
	traces.append(np.imag(trace))
	traces.append(np.absolute(trace))
	traces.append(np.angle(trace)) 
	measurement_power_arr = np.linspace(measurement_power, measurement_power, numpoints)
	data.add_data_point(measurement_power_arr, freq_array, *traces)
	generate_meta_file(no_of_measurement_power+1, measurement_power)
	measurement_power_progress_bar.update(no_of_measurement_power+1)

data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
print(time.time()-start)

# znb.rf_off()






