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
######################################

def copy_script(once):
  if once:
    shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data.get_filename())+1)],os.path.basename(sys.argv[0])))


#############################
# Initialize Instruments
#############################
dg = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA194405642::INSTR')
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset = True)


#############################
# Setting up file and msmts
#############################

filename = raw_input("Filename : ")

# DG sweep parameters
drive_start_freq = 10.6*MHz
drive_stop_freq = 10.8*MHz
resolution = 50*Hz
drive_start_power = 5 #V
drive_stop_power = 5
drive_power_numpoint = 1

RBW = resolution*2


drive_numpoints = int(abs(drive_stop_freq - drive_start_freq )/resolution + 1)

#cavity pump frequency
#### SMF parameters
smf_freq = 5965*MHz
smf_power= 11


# setup DG as source
dg.write(':ROSC:SOUR EXT')
qt.msleep(3)
dg.write(':OUTP1:LOAD 50')
dg.write(':SOUR1:APPL:SIN 10e6, %d'%drive_start_power)
dg.write(':OUTP1 ON')

# Prepare SMF
smf.set_frequency(smf_freq)
smf.set_source_power(smf_power)
smf.rf_on()

fsv.set_centerfrequency(drive_start_freq )

go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'

### SETTING UP DATA FILE
data=qt.Data(name=filename)
data.add_coordinate('Drive Power', units='dBm')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_value('Record Power')

drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
drive_power_array = np.linspace(drive_start_power, drive_stop_power, drive_power_numpoint)

qt.mstart()
once = True

########### FSV READY
fsv.set_centerfrequency(drive_start_freq )
fsv.set_span(0)
fsv.set_sweep_points(101)
fsv.set_bandwidth(RBW)
# fsv.set_continuous_sweep(False)

qt.msleep(5)


sweep_time = fsv.get_sweep_time()


for div_power in drive_power_array:
	start_time = time.time()
	# dg.(div_power)
	power_list = np.linspace(div_power, div_power, num=drive_numpoints)
	traces=[]
	for index, drive_freq in enumerate(drive_freq_array):
		print('%d/%d'%(index+1,len(drive_freq_array)), end='\r')
		dg.write(':SOUR1:APPL:SIN %f'%drive_freq)
		dg.write('*WAI')
		fsv.set_centerfrequency(drive_freq )
		fsv.w('*WAI')
		# qt.msleep(0.05)
		fsv.run_single()
		# qt.msleep(0.05)
		fsv.set_marker_frequency(drive_freq)
		# qt.msleep(sweep_time+0.1)  # UPDATE this based on sweep time
		_, power_record = fsv.get_max_freqs(1)
		traces.append(power_record[0])
		
	end_time = time.time()
	data.add_data_point(power_list, drive_freq_array, traces, meta = True)
	# generate_meta_file()
	print(end_time - start_time)
	copy_script(once)
	once = False


data.close_file()
dg.write(':OUTP1 OFF')
smf.rf_off()