from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import progressbar
from constants import *

def copy_script(data, once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))

#############################
# Measurement Parameters
#############################
# VNA sweep parameters

probe_center = 7.43888*GHz
probe_span = 50*MHz
probe_start = probe_center-probe_span/2
probe_stop = probe_center+probe_span/2
probe_numpoints = 151
if_bw_0 = 10*Hz
probe_power = -30


two_probe_center = 7.43888*GHz
two_probe_span = 1*Hz
two_probe_start = two_probe_center-two_probe_span/2
two_probe_stop = two_probe_center+two_probe_span/2
two_probe_numpoints = 1
two_if_bw_1 = 2*Hz
two_probe_power = -30


avg_point = 1

# SMF sweep parameters
spec_power = 0 #dBm (SMF power) 30 dB attenuation
spec_start = 5.9*GHz
spec_stop = 7.3*GHz
spec_resolution = 1*MHz
spec_numpoints = int(abs(spec_stop - spec_start)/spec_resolution + 1)

#side Band sweep

sideband_power = 0 #dBm (SMF power) 30 dB attenuation
sideband_start = 3*MHz
sideband_stop = 4*MHz
sideband_resolution = 100*Hz
sideband_numpoints = int(abs(sideband_stop - sideband_start)/sideband_resolution + 1)

# Yokogawa Parameters
current_start = 0.305e-3   # Unit (A)
current_stop = 0.305e-3 
current_numpoints = 1

#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420', address = APSYN420_ADDRESS)

# setup SMF100 as source
smf.set_frequency(spec_start)
smf.set_source_power(spec_power)
smf.rf_on()

# Setup VNA 
znb.set_external_reference(True)
znb.rf_on()
##############
#Channel No. 1
##############
znb.add_trace('S21',channel_number = 1)
znb.set_source_power(probe_power,channel_number = 1)
znb.set_start_frequency(probe_start,channel_number = 1)
znb.set_stop_frequency(probe_stop,channel_number = 1)
znb.set_numpoints(probe_numpoints,channel_number = 1)
znb.set_if_bandwidth(if_bw_0,channel_number = 1)
znb.send_trigger(channel_number = 1, wait=True)
znb.autoscale_diagram(window_number = 1)

##############
#Channel No. 2
##############

znb.add_trace('S21',channel_number = 2)
znb.set_source_power(two_probe_power,channel_number = 2)
znb.set_start_frequency(two_probe_start,channel_number = 2)
znb.set_stop_frequency(two_probe_stop,channel_number = 2)
znb.set_numpoints(two_probe_numpoints,channel_number = 2)
znb.set_if_bandwidth(two_if_bw_1,channel_number = 2)
znb.send_trigger(channel_number = 2)
qt.msleep(znb.get_sweeptime(channel_number = 2))
znb.autoscale_diagram(window_number = 2)




### SETTING UP DATA FILES

filename = raw_input('Filename : ')

go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'

data0=qt.Data(name='cavity')
data0.add_coordinate('Current', units='A')
data0.add_coordinate('Probe Frequency', units='Hz')
data0.add_value('S21 abs')


data1=qt.Data(name='2Tone_-20dBm')
data1.add_coordinate('Current', units='A')
data1.add_coordinate('Spec frequency', units='Hz')
data1.add_value('S21 real')
data1.add_value('S21 imag')
data1.add_value('S21 abs')
data1.add_value('S21 phase')


probe_freq_array = np.linspace(probe_start, probe_stop, probe_numpoints)
spec_freq_array = np.linspace(spec_start, spec_stop, spec_numpoints)
sideband_freq_array = np.linspace(sideband_start, sideband_stop, sideband_numpoints)
sweep_array = np.split(sideband_freq_array,100)

in_meta_0 = [probe_start, probe_stop, probe_numpoints, 'Probe Frequency (Hz)']
out_meta_0 = [current_stop, current_start, current_numpoints,'Current (A)']

in_meta_1 = [spec_start, spec_stop, spec_numpoints, 'Spec Frequency (Hz)']
out_meta_1 = out_meta_0

qt.mstart()
once = True


# Initial config

smf.set_source_power(spec_power)

for index in range(len(sweep_array)):
	start_time = time.time()
	sideband_list = np.linspace(sweep_array[index][0], sweep_array[index][0], num=probe_numpoints)
	znb.send_trigger(channel_number = 1,wait=True)
	res = znb.find_peak(channel_number = 1)
	trace = znb.get_data('S21',channel_number = 1)
	data0.add_data_point(sideband_list, probe_freq_array, np.abs(trace))
	data0.metagen2D(in_meta_0, out_meta_0)
	copy_script(data0, once)
	### Prepare SMF
	smf.rf_on()
	print('Peak detected at:  ', res['freq'])
	znb.set_start_frequency(res['freq']-two_probe_span/2,channel_number = 2)
	znb.set_stop_frequency(res['freq']+two_probe_span/2,channel_number = 2)
	traces=[]
	for j, spec_freq in enumerate(spec_freq_array):
		print('%d/%d'%(j+1,len(spec_freq_array)), end='\r')
		# spec_list = np.linspace(spec_freq, spec_freq, spec_numpoints)
		smf.set_frequency(spec_freq)
		znb.send_trigger(channel_number = 2)
		qt.msleep(znb.get_sweeptime(channel_number = 2))
		trace = znb.get_data('S21', channel_number = 2)
		traces.append(np.absolute(trace))
	q_freq = spec_freq_array[np.argmin(traces)]
	sideband_traces = [[],[],[],[]]
	for i, sideband in enumerate(sweep_array[index]):
		print('%d/%d'%(i+1,len(sweep_array[index])), end='\r')
		# spec_list = np.linspace(spec_freq, spec_freq, spec_numpoints)
		smf.set_frequency(q_freq + sideband)
		znb.send_trigger(channel_number = 2)
		qt.msleep(znb.get_sweeptime(channel_number = 2))
		trace = znb.get_data('S21', channel_number = 2)
		sideband_traces[0].append(np.real(trace))
		sideband_traces[1].append(np.imag(trace))
		sideband_traces[2].append(np.absolute(trace))
		sideband_traces[3].append(np.angle(trace))
	end_time = time.time()
	sideband_list = np.linspace(sweep_array[i][0], sweep_array[i][0], num=len(sweep_array[index]))
	data1.add_data_point(sideband_list, np.arange(len(sweep_array[index])), sideband_traces[0], sideband_traces[1], sideband_traces[2], sideband_traces[3])
	copy_script(data1, once)
	data1.metagen2D(in_meta_1, out_meta_1)
	smf.rf_off()
	print(end_time - start_time)
	once = False

data0.close_file()
data1.close_file()
# zbn.rf_off()

