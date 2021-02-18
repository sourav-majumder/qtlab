import qt
import numpy as np
import os
import shutil
import sys
import progressbar
from constants import *


def meta_3D():
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (probe_points, probe_start_freq, probe_stop_freq, 'Probe Frequency(Hz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (freq_points, start_freq, stop_freq, 'Pump Frequency (Hz)'))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
    	(power_points, start_power, stop_power, 'Pump Power (dBm)'))

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


znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address='TCPIP0::192.168.1.3::INSTR')
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)


##############
# SMF parameters for the Pump
center_freq = 5.78*GHz 
pump_span = 200*MHz
start_freq = center_freq - pump_span/2
stop_freq = center_freq + pump_span/2
freq_points = 101

start_power = 4
stop_power = 9
power_points = 6


###### VNA
# Signal setup

probe_freq = center_freq
probe_span = 200*MHz
probe_points = 101
if_bw = 100*Hz
probe_power = -35

probe_start_freq = probe_freq - probe_span/2
probe_stop_freq = probe_freq + probe_span/2

#   smf_setup
smf.set_frequency(start_freq)
smf.set_source_power(start_power)
smf.rf_on()

#   vna_setup
znb.reset()
znb.set_sweep_mode('cont')
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_start_frequency(probe_start_freq)
znb.set_stop_frequency(probe_stop_freq)
znb.set_numpoints(probe_points)
znb.set_if_bandwidth(if_bw)
znb.set_source_power(probe_power)
znb.add_trace('S21')
znb.rf_on()


#  Data file setup
data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
data.add_coordinate('Power', units='dBm')
data.add_coordinate('Pump Frequency', units='Hz')
data.add_coordinate('Signal Frequency', units='Hz')
data.add_value('S21 abs')


power_list = np.linspace(start_power, stop_power, power_points)
freq_list = np.linspace(start_freq, stop_freq, freq_points)
signal_freq_list = np.linspace(probe_start_freq, probe_stop_freq, probe_points)


znb.set_sweep_mode('single')
once = True

progress_bar = progressbar.ProgressBar(maxval=len(power_list), \
        widgets=['Progress: ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
progress_bar.start()


for idx, power in enumerate(power_list):
	smf.set_source_power(power)
	dummy_power_list = np.linspace(power,power,probe_points)
	for freq in freq_list:
		dummy_freq_list = np.linspace(freq,freq,probe_points)
		smf.set_frequency(freq)
		znb.send_trigger(wait=True)
		trace = znb.get_data('S21')
		znb.autoscale()
		data.add_data_point(dummy_power_list, dummy_freq_list, signal_freq_list, np.absolute(trace))
		meta_3D()
		copy_script(once)
		once = False

	progress_bar.update(idx+1)


data.close_file(sys.argv[0])
progress_bar.finish()

smf.rf_off()