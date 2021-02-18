# Power sweep script for qubit

import qt
import numpy as np
import shutil
import sys
import os
from constants import *


########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

# Nmeas = 1 #No. of Measurements
# paramList = [[]]*Nmeas
# average_points = 1
s_params=['S21']

##################################F
centre_freq=39.5*MHz
span=1*MHz
VNA_power=12 #dBm
if_bw= 50
num_points= 10001
step=1*MHz
num_step=37

SMF_power= 14 #dBm
SMF_freq= 4.98208*GHz
filename= 'Homodyne_10dBm_VNA_6.5VOLT_DC'

#format for params [start, stop,    num_points,  start_power,   end_power,    power_points,   if_bw,    name_of_data_file]
# paramList[0] =     [centre_freq-span/2, centre_freq+span/2,  num_points,         VNA_power,            VNA_power,          65,             10,    'Homodyne_cavity_power_sweep']
#############################################################

#create the instrument
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = 'TCPIP0::192.168.1.4::INSTR', reset=False)
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
rig = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
# rig.output_on(1)
# rig.output_on(2)

smf.reset()
smf.set_source_power(SMF_power)
smf.set_frequency(SMF_freq)
smf.rf_on()

znb.reset()
znb.set_sweep_mode('single')
znb.set_external_reference(True)
znb.set_if_bandwidth(if_bw)
znb.rf_on()

# for param in paramList:

	# start_freq = param[0]
	# stop_freq = param[1]
	# num_points = param[2]
	# start_power = param[3]
	# end_power = param[4]
	# power_points = param[5]
	# if_bw= bandwidth(start_power) #param[6]
	# filename = param[7]
	
	#znb.set_default_channel_config()
znb.set_start_frequency(centre_freq-span/2)
znb.set_stop_frequency(centre_freq+span/2)
znb.set_source_power(VNA_power)
znb.set_numpoints(num_points)
znb.add_trace('S21')
znb.send_trigger(wait=True)
znb.autoscale()

	### SETTING UP DATA FILE
data=qt.Data(name=filename)

data.add_coordinate('Cent_frequency', units='Hz')
data.add_coordinate('Index', units='NA')
data.add_value('frequency', units='Hz')
# data.add_value('S21 phase')

for s_param in s_params:
	data.add_value('%s real' % s_param.strip().upper())
	data.add_value('%s imag' % s_param.strip().upper())
	data.add_value('%s abs' % s_param.strip().upper())
	data.add_value('%s phase' % s_param.strip().upper())


	
cent_freq_list = np.linspace(centre_freq, centre_freq-(step*num_step), num_step+1)
freq_array = np.linspace(centre_freq-span/2, centre_freq+span/2, num=num_points)
qt.mstart()

	# Outer loop : Power sweep
index_count = 0
for freq in cent_freq_list:
	print index_count
	index_count+=1
	# print 'freq: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
	qt.msleep(0.1)
	znb.set_start_frequency(freq-span/2)
	znb.set_stop_frequency(freq+span/2)
	znb.send_trigger(wait=True)
	znb.autoscale()
	traces = []
	for s_param in s_params:
		trace = znb.get_data(s_param)
		traces.append(np.real(trace))
		traces.append(np.imag(trace))
		traces.append(np.absolute(trace))
		traces.append(np.angle(trace))
	cent_freq_array=np.linspace(freq,freq,num_points)
	freq_array = np.linspace(freq-span/2, freq+span/2, num=num_points)
	ind_array = np.linspace(1,num_points,num_points)
	data.add_data_point(cent_freq_array, ind_array, freq_array, *traces, meta=True)

	#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
# znb.rf_off()
data.close_file()
#sweep_gate(0.0)
rig.all_outputs_off()
znb.rf_off()
smf.rf_off()
