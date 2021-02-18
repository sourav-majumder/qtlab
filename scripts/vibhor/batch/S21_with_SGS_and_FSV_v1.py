from __future__ import print_function

import qt
import shutil
import sys
import os
import time
import matplotlib.pyplot as plt
from constants import *


def bandwidth(power):
    if power<=-55 and power>=-60:
        return 3
    elif power<=-50 and power>-55:
        return 5
    elif power<=-45 and power>-50:
        return 10
    elif power<=-35 and power>-45:
        return 50
    elif power<=-25 and power>-35:
        return 30
    elif power<=-15 and power>-25:
        return 50
    elif power<=-5 and power>-15:
        return 100
    elif power<=12 and power>-5:
        return 200
    else:
    	return 300



def copy_script(once):
	if once:
		shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))

def meta(once):
	if once:
		data.metagen2D(in_meta, out_meta)
#############################
# Initialize Instruments
#############################
rig = qt.instruments.create('DP832A', 'Rigol_DP832A', address='TCPIP0::192.168.1.5::INSTR')
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS, reset=True)
smf = qt.instruments.create('sgs', 'RS_SGS100A', address = 'TCPIP0::rssgs100a111509::inst0::INSTR')
smfreal = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = 'TCPIP0::192.168.1.4::INSTR', reset=False)
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
outer_meta_info = "SGS power"
outer_start = -35
outer_stop  = -5
# outer_resolution = 2
outer_len = 16 #int(abs(outer_stop - outer_start)/outer_resolution + 1)


# Inner-most loop
# SGS frequency

inner_meta_info = "Freq (Hz)" 
inner_start = 25.63*MHz - 100*kHz
inner_stop = 25.63*MHz + 100*kHz
# nner_resolution = 2000
inner_len = 1001  #int(abs(inner_stop - inner_start)/inner_resolution + 1)
innerloop = np.linspace(inner_start,inner_stop,inner_len)

### Other FSV variables:
## FSV parameters
center_frequency = inner_start
span = 0*Hz
RBW = 30*Hz
numpoints = 101
ref_level = -50 #dBm


# Prepare FSV
fsv.set_centerfrequency(center_frequency)
fsv.set_span(span)
fsv.set_bandwidth(RBW)
fsv.set_sweep_points(numpoints)
fsv.set_referencelevel(ref_level)
fsv.set_marker_frequency(center_frequency)


# Prepare SMF
smf.set_frequency(inner_start)
smf.set_power(outer_start)
# smf.rf_on()

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

rev_loop = np.flip(innerloop, 0)

in_meta = [inner_start, inner_stop, inner_len, 'Frequency (Hz)']
in_meta_rev = [inner_stop, inner_start, inner_len, 'Frequency (Hz)']
out_meta = [outer_stop, outer_start, outer_len*2,'Power (dBm)']

qt.mstart()
once = True


rig.output_on(2)
smf.set_status('on')
smfreal.rf_on()

qt.msleep(2)


sweep_time = fsv.get_sweep_time()


for outer in outerloop:
	start_time = time.time()
	smf.set_power(outer)
	power_list = np.linspace(outer, outer, inner_len)
	fsv.set_bandwidth(bandwidth(outer))
	qt.msleep(1)

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

	trace =[]
	for index, inner in enumerate(rev_loop):
		print('%d/%d'%(index+1,len(rev_loop)), end='\r')
		smf.set_frequency(inner)
		qt.msleep(0.05)
		fsv.set_centerfrequency(inner)
		fsv.w('*WAI')
		fsv.run_single()
		fsv.set_marker_frequency(inner)
		_, power_record = fsv.get_max_freqs(1)
		trace.append(power_record[0])
		# print(trace)
	end_time = time.time()

	data.add_data_point(power_list, rev_loop, trace)



	copy_script(once)
	meta(once)
	once = False


data.close_file()
rig.output_off(2)
smf.set_status('off')
smfreal.rf_off()