'''
attenuation after VNA is  30dBm
attenuation after SMF is  40dBm
one amplifier in use 30dBm gain

'''
from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import visa
# from future import print_function
################################
rm = visa.ResourceManager()
################################


from constants import *

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (drive_numpoints, drive_start_freq, drive_stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (DG_drive_numpoints, DG_drive_stop_freq, DG_drive_start_freq, 'DG (Hz)'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))


def r(list1, list2):
	return [ np.sqrt(x**2+y**2) for x, y in zip(list1, list2) ]



#############################
# Measurement Parameters
#############################
# VNA sweep parameters
probe_center = 6.004050*GHz
probe_span = 1*Hz
probe_start_freq = probe_center - probe_span/2
probe_stop_freq = probe_center + probe_span/2
probe_numpoints = 1
if_bw = 5*Hz
probe_power = -5 # 30 dB att + 1 dB cab;e + 6 dir coupler
s_params = ['S21']
filename = raw_input('Filename : ')
avg_point = 1

# SMF sweep parameters
drive_start_freq = 4.8*GHz
drive_stop_freq = 5*GHz
resolution = 1*MHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)
drive_power = 5

# DG sweep parameters
DG_drive_start_freq = 6.60127*MHz
DG_drive_stop_freq = 6.60135*MHz
DG_resolution = 2*Hz
DG_drive_numpoints = int(abs(DG_drive_stop_freq - DG_drive_start_freq)/DG_resolution + 1)
DG_drive_power = 10 #Volt




#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
dg = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA194405642::INSTR')

## DG READY
dg.write(':SOUR1:FREQ %f'%DG_drive_start_freq)
dg.write(':SOUR1:VOLT %f'%DG_drive_power)
dg.write(':OUTP1:LOAD 50')
dg.write(':OUTP1 ON')
qt.msleep(1)

# setup SMF100 as source
smf.set_frequency(drive_start_freq)
smf.set_source_power(drive_power)

# Setup VNA as source
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_start_frequency(probe_start_freq)
znb.set_stop_frequency(probe_stop_freq)
znb.set_numpoints(probe_numpoints)
znb.set_if_bandwidth(if_bw)
znb.set_source_power(probe_power)
znb.add_trace('S21')

# Turn on sources
znb.rf_on()
smf.rf_on()

# Test trigger
znb.send_trigger(wait=True)
# znb.autoscale()
go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'

### SETTING UP DATA FILE
data=qt.Data(name=filename)
# data.add_comment('No. of repeated measurements for average is 60')
data.add_coordinate('Probe Power', units='dBm')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')


DG_freq_array = np.linspace(DG_drive_start_freq, DG_drive_stop_freq, DG_drive_numpoints)
drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
# probe_power_array = np.linspace(probe_start_power, probe_stop_power, probe_power_numpoint)

qt.mstart()

#num_avs = 0
once = True


for dg_freq in DG_freq_array:
	start_time = time.time()
	dg.write(':SOUR1:FREQ %f'%dg_freq)
	qt.msleep(0.1)
	# znb.set_source_power(prob_power)
	dg_freq_list = np.linspace(dg_freq, dg_freq, num=drive_numpoints)
	traces=[[],[],[],[]]
	for index, drive_freq in enumerate(drive_freq_array):
		# print('%d/%d' %(index+1,len(drive_freq_array)), end ='\r')
		print('%d/%d'%(index+1,len(drive_freq_array)), end='\r')
		traces_sum=[0,0,0,0]
		smf.set_frequency(drive_freq)
		for i in range(avg_point):
			znb.send_trigger(wait=True)
			trace = znb.get_data('S21')
			traces_sum[0]+=np.real(trace)
			traces_sum[1]+=np.imag(trace) 
			traces_sum[2]+=np.absolute(trace)
    		traces_sum[3]+=np.angle(trace)   
		traces[0].append(traces_sum[0][0]/avg_point)
		traces[1].append(traces_sum[1][0]/avg_point)
		traces[2].append(traces_sum[2][0]/avg_point)
		traces[3].append(traces_sum[3][0]/avg_point)
	end_time = time.time()
	data.add_data_point(dg_freq_list, drive_freq_array, traces[0], traces[1], r(traces[0], traces[1]), traces[3])
	generate_meta_file()
	copy_script(once);once = False
	print(end_time - start_time)



smf.rf_off()
dg.write(':OUTP1 OFF')

#create script in data directory
# shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])