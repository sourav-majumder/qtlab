'''
attenuation after VNA is  40dBm
attenuation after SMF is  26dBm
one amplifier in use 30dBm gain

'''

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
            (ac_numpoints, stop_power, start_power, 'dBm'))
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
# VNA sweep parameters
probe_center = 7.35310*GHz
probe_span = 2*Hz
probe_start_freq = probe_center - probe_span/2
probe_stop_freq = probe_center + probe_span/2
probe_numpoints = 1
if_bw = 10*Hz

probe_power = -27 #dBm 50dB attenuation at VNA
probe_power_numpoint = 21
s_params = ['S21']
filename = 'three_tone_without_lockin_ref'
avg_point = 10

# SMF sweep parameters
start_power = 15 #dBm 30dB attenuation at SMF
stop_power = -5 #dBm 30dB attenuation at SMF
ac_numpoints = 21
ac_freq = probe_center + 67*MHz


#APS parameters
drive_start_freq = 5.600*GHz
drive_stop_freq = 5.670*GHz
resolution = 0.25*MHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)
drive_power = 23 #dBm 70dB attenuation + variable attenuator




#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)
aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS)

# setup SMF100 as source
smf.set_frequency(ac_freq)
smf.set_source_power(start_power)

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

# Test trigger
znb.send_trigger(wait=True)
# znb.autoscale()
# go_on = raw_input('Continue? [y/n] ')

# assert go_on.strip().upper() != 'N'

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
# probe_power_array = np.linspace(probe_start_power, probe_stop_power, probe_power_numpoint)
ac_power_array = np.linspace(start_power, stop_power, ac_numpoints)
qt.mstart()

#traces_sum = [np.zeros(drive_numpoints), np.zeros(drive_numpoints)]

#num_avs = 0
znb.set_source_power(probe_power)

for ac_power in ac_power_array:
	start_time = time.time()
	smf.set_source_power(ac_power)
	power_list = np.linspace(ac_power, ac_power, num=drive_numpoints)
	traces=[[],[],[],[]]
	for drive_freq in drive_freq_array:
		traces_sum=[0,0]
		aps.set_frequency(drive_freq)
		for i in range(avg_point):
			znb.send_trigger(wait=True)
			trace = znb.get_data('S21')
			traces_sum[0]+=np.real(trace)
			traces_sum[1]+=np.imag(trace)    
		traces[0].append(traces_sum[0][0]/avg_point)
		traces[1].append(traces_sum[1][0]/avg_point)
		traces[2].append(np.abs(traces[0][-1] + 1j*traces[1][-1]))
		traces[3].append(np.angle(traces[0][-1] + 1j*traces[1][-1]))
	end_time = time.time()
	data.add_data_point(power_list, drive_freq_array, traces[0], traces[1], traces[2], traces[3])
	generate_meta_file()
	print(end_time - start_time)



# smf.rf_off()
# znb.rf_off()
#print num_avs

# drive_array = np.linspace(drive_freq, drive_freq, probe_numpoints)
# print np.array(traces[0]).shape


#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])