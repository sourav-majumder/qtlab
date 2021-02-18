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
center_freq = 2*7.414667*GHz #Pump freq

probe_start_freq = 7.36*GHz
probe_stop_freq = 7.46*GHz
probe_sweep_point = 201
probe_power = -50 #dBm
probe_bandwidth = 70

drive_freq_point = 111
drive_start_freq = center_freq - 100*MHz
drive_stop_freq = center_freq + 10*MHz
drive_power = -2 #dBm


smf.set_frequency(center_freq)
smf.set_source_power(drive_power)
znb.set_external_reference(True)

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
	
	pump_list = np.linspace(drive_start_freq, drive_stop_freq, drive_freq_point)
	freq_array = np.linspace(probe_start_freq, probe_stop_freq, num=probe_sweep_point)
	qt.mstart()
	# znb.rf_on()

	# Outer loop : Power sweep
	index_count = 0
	for pump in pump_list:
		print index_count
		index_count+=1
		#print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
		# qt.msleep(30)
		smf.set_frequency(pump)
		znb.send_trigger(wait=True)
		znb.autoscale()
		traces = []
		for s_param in s_params:
			trace = znb.get_data(s_param)
			traces.append(np.real(trace))
			traces.append(np.imag(trace))
			traces.append(np.absolute(trace))
			traces.append(np.angle(trace))
		pump_array = np.linspace(pump, pump, num=probe_sweep_point)
		data.add_data_point(pump_array, freq_array, *traces, meta=True)

	#create script in data directory
	shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))
	# copy_script(sys.argv[0], filename)
	# znb.rf_off()
	data.close_file(sys.argv[0])

smf.rf_off()
# znb.rf_off()