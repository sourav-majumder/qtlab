from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import numpy as np


import plot
pl = plot.get_plot()
pl = pl.get_plot()
pl.clear()

from constants import *

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
probe_center = 7.45637*GHz
probe_span = 1*Hz
probe_start_freq = probe_center-probe_span/2
probe_stop_freq = probe_center+probe_span/2
probe_numpoints = 1
if_bw = 10*Hz
probe_power = -40  #  6+1+1 dir coupler
s_params = ['S21']
avg_point = 1
filename = raw_input('Filename : ')

# SMF sweep parameters6
# 
drive_start_freq = 7.0*GHz
drive_stop_freq = 7.2*GHz
resolution = 10*MHz
drive_numpoints = int(round(abs(drive_stop_freq - drive_start_freq)/resolution + 1))
drive_start_power = -20
drive_stop_power = -20
drive_power_numpoint = 3


#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)

# setup SMF100 as source
smf.set_frequency(drive_start_freq)
smf.set_source_power(drive_start_power)

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



drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
drive_power_array = np.linspace(drive_start_power, drive_stop_power, drive_power_numpoint)

qt.mstart()

#traces_sum = [np.zeros(drive_numpoints), np.zeros(drive_numpoints)]

#num_avs = 0
once = True
plt.figure(figsize = (8,4))
plt.clf()

for div_power in drive_power_array:
	start_time = time.time()
	smf.set_source_power(div_power)
	power_list = np.linspace(div_power, div_power, num=drive_numpoints)
	traces=[[],[],[],[]]
	# raw_input('press enter to continue')
	x_vals = []
	y_vals = []

	for index, drive_freq in enumerate(drive_freq_array):
		plt.cla()

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
		x = traces_sum[0][0]/avg_point
		y = traces_sum[1][0]/avg_point
		r = traces_sum[2][0]/avg_point
		t = traces_sum[3][0]/avg_point    
		
		data.add_data_point(div_power, drive_freq, x, y, r, t)
		pl.add_trace(drive_freq, r)
		pl.update()


	end_time = time.time()
	# data.add_data_point(power_list, drive_freq_array, traces[0], traces[1], traces[2], traces[3])
	generate_meta_file()
	copy_script(once);once = False
	
	



	print(end_time - start_time)



#print num_avs

# drive_array = np.linspace(drive_freq, drive_freq, probe_numpoints)
# print np.array(traces[0]).shape
smf.rf_off()

#create script in data directory
# shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])