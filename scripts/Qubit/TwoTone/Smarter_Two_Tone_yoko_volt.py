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

probe_center = 5.9966*GHz
probe_span = 50*MHz
probe_start = probe_center-probe_span/2
probe_stop = probe_center+probe_span/2
probe_numpoints = 201
if_bw_0 = 2*Hz
probe_power = -28  #  -6-1-1 attn
 

two_probe_center = 5.9966*GHz
two_probe_span = 1*Hz
two_probe_start = two_probe_center-two_probe_span/2
two_probe_stop = two_probe_center+two_probe_span/2
two_probe_numpoints = 1
two_if_bw_1 = 5*Hz
two_probe_power = -28  #  -6-1-1 attn


avg_point = 1

# SMF sweep parameters
spec_power = -15 #dBm (SMF power) 0 dB attenuation
spec_start = 6.4*GHz
spec_stop = 6.7*GHz
spec_resolution = 1*MHz
spec_numpoints = int(round(abs(spec_stop - spec_start)/spec_resolution) + 1)

# Yokogawa Parameters
current_start = -0.2e-3  # Unit (mA)
current_stop = -0.1e-3 
current_numpoints = 11

#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
qs =  qt.instruments.create('GS200', 'Yokogawa_GS200', address = GS200_ADDRESS)
rigol = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')


# setup SMF100 as source
smf.set_frequency(spec_start)
smf.set_source_power(spec_power)


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

data0=qt.Data(name='cavity {}'.format(filename))
data0.add_coordinate('Current', units='A')
data0.add_coordinate('Probe Frequency', units='Hz')
data0.add_value('S21 abs')


data1=qt.Data(name='Qubit {}'.format(filename))
data1.add_coordinate('Current', units='A')
data1.add_coordinate('Spec frequency', units='Hz')
data1.add_value('S21 real')
data1.add_value('S21 imag')
data1.add_value('S21 abs')
data1.add_value('S21 phase')


probe_freq_array = np.linspace(probe_start, probe_stop, probe_numpoints)
spec_freq_array = np.linspace(spec_start, spec_stop, spec_numpoints)
current_array = np.linspace(current_start, current_stop, current_numpoints)

in_meta_0 = [probe_start, probe_stop, probe_numpoints, 'Probe Frequency (Hz)']
out_meta_0 = [current_stop, current_start, current_numpoints,'Current (A)']

in_meta_1 = [spec_start, spec_stop, spec_numpoints, 'Spec Frequency (Hz)']
out_meta_1 = out_meta_0

qt.mstart()
qs.set_output(True)
once = True
autoscale_once = True

# Initial config

smf.set_source_power(spec_power)

for current in current_array:
	start_time = time.time()
	current_list = np.linspace(current, current, num=probe_numpoints)
	qs.sweep_current(current, delay = 0.05)
	znb.send_trigger(channel_number = 1,wait=True)
	res = znb.find_peak(channel_number = 1)
	trace = znb.get_data('S21',channel_number = 1)
	data0.add_data_point(current_list, probe_freq_array, np.abs(trace))
	data0.metagen2D(in_meta_0, out_meta_0)
	copy_script(data0, once)
	### Prepare SMF
	smf.rf_on()
	print('Peak detected at:  ', res['freq'])
	znb.set_start_frequency(res['freq']-two_probe_span/2,channel_number = 2)
	znb.set_stop_frequency(res['freq']+two_probe_span/2,channel_number = 2)
	traces=[[],[],[],[]]
	for index, spec_freq in enumerate(spec_freq_array):
		print('%d/%d'%(index+1,len(spec_freq_array)), end='\r')
		# spec_list = np.linspace(spec_freq, spec_freq, spec_numpoints)
		traces_sum=[0,0,0,0]
		smf.set_frequency(spec_freq)
		for i in range(avg_point):
			znb.send_trigger(channel_number = 2)
			qt.msleep(znb.get_sweeptime(channel_number = 2) + 0.01)
			if autoscale_once:
				znb.autoscale_diagram(window_number = 2)
			autoscale_once = False
			trace = znb.get_data('S21', channel_number = 2)
			traces_sum[0]+=np.real(trace)
			traces_sum[1]+=np.imag(trace)
			traces_sum[2]+=np.absolute(trace)
			traces_sum[3]+=np.angle(trace)    
		traces[0].append(traces_sum[0][0]/avg_point)
		traces[1].append(traces_sum[1][0]/avg_point)
		traces[2].append(traces_sum[2][0]/avg_point)
		traces[3].append(traces_sum[3][0]/avg_point)
	end_time = time.time()
	current_list = np.linspace(current, current, num=spec_numpoints)
	data1.add_data_point(current_list, spec_freq_array, traces[0], traces[1], traces[2], traces[3])
	copy_script(data1, once)
	data1.metagen2D(in_meta_1, out_meta_1)
	smf.rf_off()
	print(end_time - start_time)
	once = False
	autoscale_once = True

data0.close_file()
data1.close_file()
znb.rf_off()
smf.rf_off()
rigol.output_off(2)

