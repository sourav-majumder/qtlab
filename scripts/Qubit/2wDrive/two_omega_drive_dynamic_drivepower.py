# Power sweep script for qubit

import qt
import numpy as np
import shutil
import sys
import os
from constants import *





########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

Nmeas = 1 #No. of Measurements
paramList = [[]]*Nmeas
average_points = 1
s_params=['S21']
# center = 7.8*GHz
# span = 50*MHz


#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
znb.reset()
znb.set_sweep_mode('single')
center_freq = (7.6208+7.391)*0.5*GHz

probe_start_freq = 7.32*GHz
probe_stop_freq = 7.66*GHz
probe_sweep_point = 301
probe_power = -50 #dBm
probe_bandwidth = 30

drive_power_point = 81
drive_start_power = -0 #dBm
drive_stop_power = -20 #dBm

smf.set_frequency(center_freq*2 - 5*MHz)
smf.set_source_power(drive_stop_power)

filename = raw_input('Filename : ')
smf.rf_on()
znb.rf_on()



for param in paramList:
	
	#znb.set_default_channel_config()
	znb.set_start_frequency(probe_start_freq)
	znb.set_stop_frequency(probe_stop_freq)
	znb.set_source_power(probe_power)
	znb.set_numpoints(probe_sweep_point)
	znb.set_if_bandwidth(probe_bandwidth)

	for s_param in s_params:
		znb.add_trace(s_param)
	znb.send_trigger(wait=True)
	znb.autoscale()
	#qt.msleep(15)

	### SETTING UP DATA FILE
	data=qt.Data(name=filename)
	# data.add_comment('No. of repeated measurements for average is 60')
	data.add_coordinate('Power', units='dBm')
	data.add_coordinate('Frequency', units='Hz')
	for s_param in s_params:
		data.add_value('%s real' % s_param.strip().upper())
		data.add_value('%s imag' % s_param.strip().upper())
		data.add_value('%s abs' % s_param.strip().upper())
		data.add_value('%s phase' % s_param.strip().upper())
	
	power_list = np.linspace(drive_start_power, drive_stop_power, drive_power_point)
	freq_array = np.linspace(probe_start_freq, probe_stop_freq, num=probe_sweep_point)
	qt.mstart()
	# znb.rf_on()

	# Outer loop : Power sweep
	index_count = 0
	for power in power_list:
		print index_count
		index_count+=1
		#print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
		# qt.msleep(30)
		smf.set_source_power(power)
		znb.send_trigger(wait=True)
		znb.autoscale()
		traces = []
		for s_param in s_params:
			trace = znb.get_data(s_param)
			traces.append(np.real(trace))
			traces.append(np.imag(trace))
			traces.append(np.absolute(trace))
			traces.append(np.angle(trace))
		power_array = np.linspace(power, power, num=probe_sweep_point)
		data.add_data_point(power_array, freq_array, *traces, meta=True)

	#create script in data directory
	shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))
	# copy_script(sys.argv[0], filename)
	# znb.rf_off()
	data.close_file(sys.argv[0])

smf.rf_off()
znb.rf_off()