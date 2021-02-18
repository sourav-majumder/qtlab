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
drive_start_freq = 5.95378*GHz-35*kHz
drive_stop_freq = 5.95378*GHz+35*kHz
resolution = 1*kHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)
drive_start_power = -10 #dBm 40 dB attenuation at SMF
drive_stop_power = -10 #dBm
drive_power_numpoint = 1



#############################
# Initialize Instruments
#############################
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address = ZNB20_ADDRESS)

# setup SMF100 as source
smf.set_frequency(drive_start_freq)
smf.set_source_power(drive_start_power)
fsv.set_centerfrequency(drive_start_freq-100*kHz)
znb.set_center_frequency(drive_start_freq-100*kHz)

# Turn on sources
smf.rf_on()
znb.rf_on()
go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'

### SETTING UP DATA FILE
data=qt.Data(name=filename)
# data.add_comment('No. of repeated measurements for average is 60')
data.add_coordinate('Drive Power', units='dBm')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_value('Signal')
data.add_value('Floor')
data.add_value('Difference')
data.add_value('Signal (Pump off)')
data.add_value('Floor (Pump off)')
data.add_value('Difference (Pump off)')



drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
drive_power_array = np.linspace(drive_start_power, drive_stop_power, drive_power_numpoint)

qt.mstart()

#traces_sum = [np.zeros(drive_numpoints), np.zeros(drive_numpoints)]

#num_avs = 0
inst = fsv.get_instrument()

for freq in drive_freq_array:
	start_time = time.time()
	smf.set_frequency(freq)
	znb.set_center_frequency(freq-100*kHz)
	znb.send_trigger()
	fsv.set_centerfrequency(freq-100*kHz)
	freq_list = np.linspace(freq, freq, num=drive_power_numpoint)
	floor=[]
	traces=[]
	diff=[]
	traces2 = []
	floor2=[]
	diff2=[]
	for index, power in enumerate(drive_power_array):
		print('%d/%d'%(index+1,len(drive_power_array)), end='\r')
		smf.set_source_power(power)
		smf.rf_on()
		inst.write('INIT')
		qt.msleep(24)
		fsvdata = fsv.get_data()
		traces.append(fsvdata[1][50])
		floor.append(fsvdata[1][0])
		diff.append(fsvdata[1][50]-fsvdata[1][0])
		smf.rf_off()
		inst.write('INIT')
		qt.msleep(24)
		fsvdata = fsv.get_data()
		traces2.append(fsvdata[1][50])
		floor2.append(fsvdata[1][0])
		diff2.append(fsvdata[1][50]-fsvdata[1][0])
		
	end_time = time.time()
	data.add_data_point(freq_list, drive_power_array, traces, floor, diff, traces2, floor2, diff2)
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