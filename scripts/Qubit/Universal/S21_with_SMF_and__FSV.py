from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import matplotlib.pyplot as plt
from constants import *


def copy_script(once):
	if once:
		shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))

def meta(once):
	if once:
		data.metagen2D(in_meta, out_meta)
#############################
# Initialize Instruments
#############################

fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)

#############################
# Setting up file and msmts
#############################


# OuterMost loop 
outermost_meta_info = "Nothing" 
outermost_start = 0
outermost_stop  = 1  # One more than the end point you 
outermost_len  =  1

# Outer loop

#Outerloop SMF power loop
outer_meta_info = "SMF power"
outer_start = -20 
outer_stop  = -20
outer_resolution = 1
outer_len = 3 #int(abs(outer_stop - outer_start)/outer_resolution + 1)


# Inner-most loop
# SMF frequency

inner_meta_info = "Freq (Hz)" 
inner_start = 1*GHz
inner_stop = 12*GHz 
inner_resolution = 1000*MHz
inner_len = int(abs(inner_stop - inner_start)/inner_resolution + 1)
innerloop = np.linspace(inner_start,inner_stop,inner_len)

### Other FSV variables:
## FSV parameters
center_frequency = inner_start
span = 0*Hz
RBW = 100*Hz
numpoints = 101
ref_level = -70 #dBm


# Prepare FSV
fsv.set_centerfrequency(center_frequency)
fsv.set_span(span)
fsv.set_bandwidth(RBW)
fsv.set_sweep_points(numpoints)
fsv.set_referencelevel(ref_level)
fsv.set_marker_frequency(center_frequency)


# Prepare SMF
smf.set_frequency(inner_start)
smf.set_source_power(outer_start)
smf.rf_on()

### SETTING UP DATA FILE

data_file_name = raw_input('Enter name of data file: ')
data=qt.Data(name=data_file_name)
data.add_coordinate('Power', units='dBm')
data.add_coordinate('Frequency', units='Hz')
data.add_value('PSD', units = 'dBm')

go_on = raw_input('Continue? [y/n] ')
assert go_on.strip().upper() != 'N'


innerloop = np.linspace(inner_start,inner_stop,inner_len)
outerloop = np.linspace(outer_start,outer_stop,outer_len)
outermostloop = np.linspace(outermost_start,outermost_stop,outermost_len) 



in_meta = [inner_start, inner_stop, inner_len, 'Frequency (Hz)']
out_meta = [outer_stop, outer_start, outer_len,'Power (dBm)']

qt.mstart()
once = True
qt.msleep(1)


sweep_time = fsv.get_sweep_time()


for outer in outerloop:
	start_time = time.time()
	smf.set_source_power(outer)
	power_list = np.linspace(outer, outer, inner_len)
	trace=[]
	for index, inner in enumerate(innerloop):
		print('%d/%d'%(index+1,len(innerloop)), end='\r')
		smf.set_frequency(inner)
		qt.msleep(0.05)
		fsv.set_centerfrequency(inner)
		fsv.w('*WAI')
		fsv.run_single()
		fsv.set_marker_frequency(inner)
		_, power_record = fsv.get_max_freqs(1)
		trace.append(power_record[0])
	end_time = time.time()
	data.add_data_point(power_list, innerloop, trace)
	print(end_time - start_time)
	plt.plot(innerloop, trace)
	plt.grid()
	plt.show()
	copy_script(once)
	meta(once)
	once = False


data.close_file()
smf.rf_off()