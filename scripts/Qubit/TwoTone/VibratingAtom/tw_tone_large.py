from __future__ import print_function

import qt
import shutil
import sys
import os
import time

from constants import *

def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (len(sweep_array[0]), sweep_array[0][0], sweep_array[0][-1], 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (split, sweep_array[-1][0], sweep_array[0][0], 'index'))
    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()\

def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))


#############################
# Measurement Parameters
#############################
# VNA sweep parameters
probe_center = 7.413638*GHz
probe_span = 1*Hz
probe_start_freq = probe_center-probe_span/2
probe_stop_freq = probe_center+probe_span/2
probe_numpoints = 1
if_bw = 1*Hz
probe_power = -50 #dBm 26dB attenuation at VNA
s_params = ['S21']
filename = raw_input('Filename : ')
avg_point = 1

# SMF sweep parameters
qubit_freq = 4.52142*GHz
drive_start_freq = qubit_freq - 6*MHz
drive_stop_freq = qubit_freq - 5*MHz
resolution = 10*Hz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution +1)
sideband_power = -10 #dBm 20 dB attenuation at SMF

split = 1000



#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)

# setup SMF100 as source
smf.set_frequency(drive_start_freq)
smf.set_source_power(sideband_power)

# Setup VNA as source
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_source_power(probe_power)
znb.set_start_frequency(probe_start_freq)
znb.set_stop_frequency(probe_stop_freq)
znb.set_numpoints(probe_numpoints)
znb.set_if_bandwidth(if_bw)
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
data.add_coordinate('Drive Power', units='dBm')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')
data.add_value('Sideband Freq')



drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
sweep_array = np.split(drive_freq_array[:-1],split)

qt.mstart()

#traces_sum = [np.zeros(drive_numpoints), np.zeros(drive_numpoints)]

#num_avs = 0
once = True

for index, sideband_array in enumerate(sweep_array):
	start_time = time.time()
	sideband_list = np.linspace(sideband_array[0], sideband_array[0], num=len(sideband_array))
	traces=[[],[],[],[]]
	for i, side_freq in enumerate(sideband_array):
		print('%d/%d'%(i+1,len(sideband_array)), end='\r')
		traces_sum=[0,0,0,0]
		smf.set_frequency(side_freq)
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
	data.add_data_point(sideband_list, range(len(sideband_array)), traces[0], traces[1], traces[2], traces[3], sideband_array)
	generate_meta_file()
	copy_script(once);once = False
	print(end_time - start_time)



#print num_avs

# drive_array = np.linspace(drive_freq, drive_freq, probe_numpoints)
# print np.array(traces[0]).shape


#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])