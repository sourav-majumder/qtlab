# Power sweep script for qubit

import qt
import numpy as np
import shutil
import sys
import os
from constants import *


def bandwidth(power):
    if power<=-50 and power>=-60:
        return 5
    elif power<=-40 and power>-50:
        return 20
    elif power<=-30 and power>-40:
        return 30
    elif power<=-20 and power>-30:
        return 50
    elif power<=-10 and power>-20:
        return 100
    elif power<=0 and power>-10:
        return 100
    elif power<=10 and power>0:
        return 100




########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

Nmeas = 1 #No. of Measurements
paramList = [[]]*Nmeas
average_points = 1
s_params=['S21']
# center = 7.8*GHz
# span = 50*MHz

#format for params [start, stop,    num_points,  start_power,   end_power,    power_points,   if_bw,    name_of_data_file]
paramList[0] =     [6.03795*GHz,  6.08795*GHz,  1001,         -40,            0,          21,             100,    'power_sweep_junction']
#############################################################

#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)
znb.reset()
znb.set_sweep_mode('single')

for param in paramList:

	start_freq = param[0]
	stop_freq = param[1]
	num_points = param[2]
	start_power = param[3]
	end_power = param[4]
	power_points = param[5]
	if_bw= param[6] # bandwidth(start_power)
	filename = param[7]
	
	#znb.set_default_channel_config()
	znb.set_start_frequency(start_freq)
	znb.set_stop_frequency(stop_freq)
	znb.set_source_power(start_power)
	znb.set_numpoints(num_points)

	znb.rf_on()
	for s_param in s_params:
		znb.add_trace(s_param)
	znb.send_trigger(wait=True)
	znb.autoscale()
	raw_input()
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
	
	power_list = np.linspace(start_power, end_power, power_points)
	freq_array = np.linspace(start_freq, stop_freq, num=num_points)
	qt.mstart()
	# znb.rf_on()

	# Outer loop : Power sweep
	index_count = 0
	for power in power_list:
		print index_count
		index_count+=1
		#print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
		#qt.msleep(0.1)
		znb.set_source_power(power)
		znb.set_if_bandwidth(bandwidth(power))
		znb.send_trigger(wait=True)
		znb.autoscale()
		traces = []
		for s_param in s_params:
			trace = znb.get_data(s_param)
			traces.append(np.real(trace))
			traces.append(np.imag(trace))
			traces.append(np.absolute(trace))
			traces.append(np.angle(trace))
		power_array = np.linspace(power, power, num=num_points)
		data.add_data_point(power_array, freq_array, *traces, meta=True)

	#create script in data directory
	shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
	# copy_script(sys.argv[0], filename)
	znb.rf_off()
	data.close_file(sys.argv[0])