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
# from future import print_function

from constants import *

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (drive_numpoints, drive_start_freq, drive_stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (detune_power_numpoint, detune_stop_power, detune_start_power, 'dBm'))
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





#############################
# Measurement Parameters
#############################
# VNA sweep parameters
probe_center = 7.4148*GHz
probe_span = 1*Hz
probe_start_freq = probe_center - probe_span/2
probe_stop_freq = probe_center + probe_span/2
probe_numpoints = 1
probe_power = -34
if_bw = 5*Hz

detune_start_power = -20 #dBm 30dB attenuation at VNA
detune_stop_power = 10 #dBm 30dB attenuation at VNA
detune_power_numpoint = 13
s_params = ['S21']
filename = raw_input('Filename : ')
avg_point = 1

# SMF sweep parameters
drive_start_freq = 6.23*GHz
drive_stop_freq = 6.5*GHz
resolution = 1*MHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)
drive_power = -20 #dBm 40 dB attenuation at SMF
qubit_freq = 6.27485*GHz



#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)



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
aps.rf_on()
smf.set_frequency(qubit_freq - 10*MHz)

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



drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
detune_power_array = np.linspace(detune_start_power, detune_stop_power, detune_power_numpoint)

qt.mstart()

#traces_sum = [np.zeros(drive_numpoints), np.zeros(drive_numpoints)]

#num_avs = 0
once = True


for detune_power in detune_power_array:
	start_time = time.time()
	smf.set_source_power(detune_power)
	power_list = np.linspace(detune_power, detune_power, num=drive_numpoints)
	traces=[[],[],[],[]]
	for index, drive_freq in enumerate(drive_freq_array):
		# print('%d/%d' %(index+1,len(drive_freq_array)), end ='\r')
		print('%d/%d'%(index+1,len(drive_freq_array)), end='\r')
		traces_sum=[0,0,0,0]
		aps.set_frequency(drive_freq)
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
	data.add_data_point(power_list, drive_freq_array, traces[0], traces[1], traces[2], traces[3])
	generate_meta_file()
	copy_script(once);once = False
	print(end_time - start_time)



# smf.rf_off()
znb.rf_off()
aps.rf_off()
#print num_avs

# drive_array = np.linspace(drive_freq, drive_freq, probe_numpoints)
# print np.array(traces[0]).shape


#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])