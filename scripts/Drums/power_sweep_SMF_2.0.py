# Power sweep script for qubit

import qt
import numpy as np
import shutil
import sys
import os
from constants import *


def bandwidth(power):
    if power<=-55 and power>=-60:
        return 3
    elif power<=-50 and power>-55:
        return 5
    elif power<=-45 and power>-50:
        return 10
    elif power<=-35 and power>-45:
        return 100
    elif power<=-25 and power>-35:
        return 10
    elif power<=-15 and power>-25:
        return 50
    elif power<=-5 and power>-15:
        return 50
    elif power<=5 and power>-5:
        return 50
    elif power<=17 and power>5:
        return 100
    elif power<=23 and power>17:
        return 100

# smf frequency=3.576520 GHz power=5dBm 
#gate volt= 0 volts

########## USER INPUTS FOR SETTING THE MEASUREMENT ##########

Nmeas = 1 #No. of Measurements
paramList = [[]]*Nmeas
average_points = 1
s_params=['S21']
# center = 7.8*GHz
# span = 50*MHz

#format for params [start, stop,    num_points,  ZNB_power,   if_bw,    name_of_data_file]
paramList[0] =     [3.583391*GHz-5*kHz,	3.583391*GHz+5*kHz,  1001,         -25,          50,    'Si_Drum_SMF_power_sw_Blue_OMIT_Narrow_Span_10.1MHz']
#############################################################
#format for params [start_power, stop_power, power_points, smf_freq]
paramList1 =     [-15,       -4,       12,        3.593635*GHz]
#MECH = 6.7*MHz
#30dB attenuation with circulator
#create the instrument
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = 'TCPIP0::192.168.1.4::INSTR', reset=False)
rig = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
znb.reset()
znb.set_sweep_mode('single')
znb.set_external_reference(True)
znb.rf_on()
smf.rf_on()

start_power = paramList1[0]
end_power = paramList1[1]
power_points = paramList1[2]
smf_freq = paramList1[3]

for param in paramList:

	start_freq = param[0]
	stop_freq = param[1]
	num_points = param[2]
	ZNB_power = param[3]
	# end_power = param[4]
	# power_points = param[5]
	if_bw= param[4] #param[6]
	filename = param[5]

for param in paramList:
	# start_power = param[3]
	# end_power = param[4]
	# power_points = param[5]
	#znb.set_default_channel_config()
	znb.set_start_frequency(start_freq)
	znb.set_stop_frequency(stop_freq)
	znb.set_source_power(ZNB_power)
	znb.set_numpoints(num_points)

	smf.set_frequency(smf_freq)

	for s_param in s_params:
		znb.add_trace(s_param)
	znb.send_trigger(wait=True)
	znb.autoscale()

	### SETTING UP DATA FILE
	data=qt.Data(name=filename)
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

	# Outer loop : Power sweep
	index_count = 0
	for power in power_list:
		print index_count
		index_count+=1
		print 'Power: %.2f dBm %.2f %% left                                            \r'%(power,(end_power-power)*100/(end_power-start_power)),
		qt.msleep(0.1)
		znb.set_source_power(ZNB_power)
		smf.set_source_power(power)
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
	# znb.rf_off()
	data.close_file()
#sweep_gate(0.0)
# rig.output_off(2)
# smf.rf_off()
# znb.rf_off()