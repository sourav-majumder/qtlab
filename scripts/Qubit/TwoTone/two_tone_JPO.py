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

#############################
# Measurement Parameters
#############################

filename = raw_input("Filename : ")

# SMF sweep parameters
drive_start_freq = 11.910334*GHz-450*MHz
drive_stop_freq = 11.910334*GHz+200*MHz
resolution = 1*MHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)
drive_start_power = 10 #dBm 40 dB attenuation at SMF
drive_stop_power = -20 #dBm
drive_power_numpoint = 31



#############################
# Initialize Instruments
#############################
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)

# setup SMF100 as source
smf.set_frequency(drive_start_freq)
smf.set_source_power(drive_start_power)
fsv.set_centerfrequency(drive_start_freq/2)

# Turn on sources
smf.rf_on()
go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'

### SETTING UP DATA FILE
data=qt.Data(name=filename)
# data.add_comment('No. of repeated measurements for average is 60')
data.add_coordinate('Drive Power', units='dBm')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_value('Record Frequency')
data.add_value('Record Power')



drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
drive_power_array = np.linspace(drive_start_power, drive_stop_power, drive_power_numpoint)

qt.mstart()

#traces_sum = [np.zeros(drive_numpoints), np.zeros(drive_numpoints)]

#num_avs = 0

for div_power in drive_power_array:
	start_time = time.time()
	smf.set_source_power(div_power)
	power_list = np.linspace(div_power, div_power, num=drive_numpoints)
	freqs=[]
	traces=[]
	for index, drive_freq in enumerate(drive_freq_array):
		print('%d/%d'%(index+1,len(drive_freq_array)), end='\r')
		smf.set_frequency(drive_freq)
		fsv.set_centerfrequency(drive_freq/2)
		qt.msleep(1)
		fsvdata = fsv.get_data()
		traces.append(fsvdata[1][0])
		freqs.append(fsvdata[0][0])
		
	end_time = time.time()
	data.add_data_point(power_list, drive_freq_array, freqs, traces)
	generate_meta_file()
	print(end_time - start_time)
	# qt.msleep(300)




#print num_avs

# drive_array = np.linspace(drive_freq, drive_freq, probe_numpoints)
# print np.array(traces[0]).shape


#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])