# Power sweep script for qubit

import qt
import numpy as np
import shutil
import sys
import os
from constants import *


def bandwidth(power):
    if power<=-50 and power>=-60:
        return 1
    elif power<=-40 and power>-50:
        return 100
    elif power<=-30 and power>-40:
        return 150
    elif power<=-20 and power>-30:
        return 200
    elif power<=-10 and power>-20:
        return 300
    elif power<=0 and power>-10:
        return 5
    elif power<=10 and power>0:
        return 5
    else:
    	return 50


def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))
once = True
########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

Nmeas = 1 #No. of Measurements
paramList = [[]]*Nmeas
average_points = 1
s_params=['S21']
s_param = s_params[0]
# center = 7.8*GHz
# span = 50*MHz

## See log book
###Power from VNA


#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)
znb.reset()

def power_sweep_setup(ifbw):
	znb.set_sweep_mode('cont')
	znb.set_external_reference(True)
	znb.set_sweep_type('pow')
	znb.set_start_power(start_power)
	znb.set_stop_power(stop_power)
	znb.set_numpoints(power_points)
	znb.set_if_bandwidth(ifbw)
	znb.set_frequency_fixed(1*GHz)
	znb.add_trace('S21')
	znb.set_sweep_mode('single')
	znb.send_trigger(wait=True)
	znb.rf_on()



ifbw = 2000

start_power = 8
stop_power = 4
power_points = 401

start_freq = 5*GHz
stop_freq = 7*GHz
num_points = 2001


power_sweep_setup(ifbw)

znb.autoscale()
raw_input('Press Enter')
znb.set_sweep_mode('single')


### SETTING UP DATA FILE
filename = raw_input('Enter the file name:  ')
data=qt.Data(name=filename)
# data.add_comment('No. of repeated measurements for average is 60')
data.add_coordinate('Frequency', units='Hz')
data.add_coordinate('Power', units='dBm')
data.add_value('real')
data.add_value('imag')
data.add_value('%s abs' % s_param.strip().upper())
data.add_value('%s phase' % s_param.strip().upper())
data.add_value('%s unwrap_phase' % s_param.strip().upper())
	

freq_array = np.linspace(start_freq, stop_freq, num=num_points)
power_array = np.linspace(start_power, stop_power, power_points)

qt.mstart()
# znb.rf_on()

#Outer loop : Frequency sweep
index_count = 0
for freq in freq_array:
	print index_count
	index_count+=1
	#print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
	# qt.msleep(30)
	znb.set_frequency_fixed(freq)
	znb.send_trigger(wait=True)
	znb.autoscale()
	traces = []
	trace = znb.get_data('S21')
	traces.append(np.real(trace))
	traces.append(np.imag(trace))
	traces.append(np.absolute(trace))
	traces.append(np.angle(trace))
	traces.append(np.unwrap(np.angle(trace)))

	dummy_freq_array = np.linspace(start_freq, stop_freq, power_points)
	data.add_data_point(dummy_freq_array, power_array, *traces, meta=True)
	copy_script(once)
	once = False

#create script in data directory
# shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
# znb.rf_off()
data.close_file(sys.argv[0])