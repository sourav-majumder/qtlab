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
            (probe_numpoints, probe_start_freq, probe_stop_freq, 'Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (drive_power_numpoint, drive_stop_power, drive_start_power, 'dBm'))
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
probe_center = 6.008952*GHz
probe_span = 10*MHz
probe_start_freq = probe_center-probe_span/2
probe_stop_freq = probe_center+probe_span/2
probe_numpoints = 201
if_bw = 1*Hz
probe_power = -60 #dBm 6+ 2.5dB attenuation at VNA
s_params = ['S21']
filename = raw_input('Filename : ')

# SMF sweep parameters6
drive_freq = 5.51625*GHz
drive_start_power = 10 #dBm 40 dB attenuation at SMF()
drive_stop_power = 0 #dBm
drive_power_numpoint = 6


#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)

# setup SMF100 as source
smf.set_frequency(drive_freq)

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


freq_array = np.linspace(probe_start_freq, probe_stop_freq, num=probe_numpoints)
drive_power_array = np.linspace(drive_start_power, drive_stop_power, drive_power_numpoint)

qt.mstart()

#traces_sum = [np.zeros(drive_numpoints), np.zeros(drive_numpoints)]

#num_avs = 0
once = True

index_count = 0
for div_power in drive_power_array:
	print(index_count)
	index_count+=1
	smf.set_source_power(div_power)
	power_list = np.linspace(div_power, div_power, num=probe_numpoints)
	znb.send_trigger(wait=True)
	znb.autoscale()
	traces = []
	trace = znb.get_data('S21')
	traces.append(np.real(trace))
	traces.append(np.imag(trace))
	traces.append(np.absolute(trace))
	traces.append(np.angle(trace))
	data.add_data_point(power_list, freq_array, *traces)
	generate_meta_file()
	copy_script(once);once = False




#print num_avs

# drive_array = np.linspace(drive_freq, drive_freq, probe_numpoints)
# print np.array(traces[0]).shape
smf.rf_off()

#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])