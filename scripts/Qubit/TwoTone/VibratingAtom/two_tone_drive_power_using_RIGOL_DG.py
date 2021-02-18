from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import visa 

from constants import *

################################
rm = visa.ResourceManager()
################################
dg = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA194405642::INSTR')


def generate_meta_file():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (drive_numpoints, drive_start_freq, drive_stop_freq, 'Frequency(Hz)'))
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
probe_center = 5.966*GHz
probe_span = 1*Hz
probe_start_freq = probe_center-probe_span/2
probe_stop_freq = probe_center+probe_span/2
probe_numpoints = 1
if_bw = 10*Hz
probe_power = -34
s_params = ['S21']
avg_point = 1
filename = raw_input('Filename : ')

# DG sweep parameters
# 
drive_start_freq = 6.58477*MHz-100
drive_stop_freq = 6.58477*MHz+100
resolution = 1*Hz
drive_numpoints = int(round(abs(drive_stop_freq - drive_start_freq)/resolution + 1))
drive_start_power =  7 #V
drive_stop_power = 7 #V
drive_power_numpoint = 2


#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)

# setup DG as source

dg.write(':SOUR1:APPL:SIN 5e6, %f'%drive_start_power)
dg.write(':OUTP1 ON')
qt.msleep(1)

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




# Test trigger
znb.send_trigger(wait=True)

go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'

### SETTING UP DATA FILE
data=qt.Data(name=filename)

data.add_coordinate('Drive Power', units='Volts')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_value('S21 real')
data.add_value('S21 imag')
data.add_value('S21 abs')
data.add_value('S21 phase')

drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
drive_power_array = np.linspace(drive_start_power, drive_stop_power, drive_power_numpoint)

qt.mstart()
once = True

for div_power in drive_power_array:
	start_time = time.time()
	dg.write(':SOUR1:VOLT %f'%div_power)
	power_list = np.linspace(div_power, div_power, num=drive_numpoints)
	traces=[[],[],[],[]]
	for index, drive_freq in enumerate(drive_freq_array):
		print('%d/%d'%(index+1,len(drive_freq_array)), end='\r')
		traces_sum=[0,0,0,0]
		dg.write(':SOUR1:FREQ %f'%drive_freq)
		qt.msleep(1)
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

dg.write(':OUTP1 OFF')
data.close_file(sys.argv[0])