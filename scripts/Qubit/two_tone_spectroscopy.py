import qt
import shutil
import sys
import os

from constants import *

#############################
# Measurement Parameters
#############################
# VNA sweep parameters
probe_center = 6.08*GHz
probe_span = 1*Hz
probe_start_freq = probe_center-probe_span/2
probe_stop_freq = probe_center+probe_span/2
probe_numpoints = 1
if_bw = 100*Hz
probe_power = -24 #dBm
s_params = ['S21']
filename = 'two_tone_spectroscopy_4.8_to_5.8_GHz'

# SMF sweep parameters
drive_start_freq = 4.8*GHz
drive_stop_freq = 5.1*GHz
resolution = 25*kHz
drive_numpoints = abs(drive_stop_freq - drive_start_freq)/resolution + 1
drive_power = 0 #dBm

#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS, reset=True)

# setup SMF100 as source
smf.set_frequency(drive_start_freq)
smf.set_source_power(drive_power) # dBm

# Setup VNA as source
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_source_power(probe_power)
znb.set_start_frequency(probe_start_freq)
znb.set_stop_frequency(probe_stop_freq)
znb.set_numpoints(probe_numpoints)
znb.set_if_bandwidth(if_bw)
for s_param in s_params:
		znb.add_trace(s_param)

# Turn on sources
znb.rf_on()
smf.rf_on()

# Test trigger
znb.send_trigger(wait=True)
znb.autoscale()
go_on = raw_input('Continue? [y/n] ')

assert go_on.strip().upper() != 'N'

### SETTING UP DATA FILE
data=qt.Data(name=filename)
# data.add_comment('No. of repeated measurements for average is 60')
data.add_coordinate('Drive Frequency', units='Hz')
data.add_coordinate('Probe Frequency', units='Hz')
for s_param in s_params:
	data.add_value('%s real' % s_param.strip().upper())
	data.add_value('%s imag' % s_param.strip().upper())
	data.add_value('%s abs' % s_param.strip().upper())
	data.add_value('%s phase' % s_param.strip().upper())

drive_freq_array = np.linspace(drive_start_freq, drive_stop_freq, drive_numpoints)
probe_array = np.linspace(probe_start_freq, probe_stop_freq, probe_numpoints)

qt.mstart()

for drive_freq in drive_freq_array:
	smf.set_frequency(drive_freq)
	znb.send_trigger(wait=True)
	znb.autoscale()
	traces = []
	for s_param in s_params:
		trace = znb.get_data(s_param)
		traces.append(np.real(trace))
		traces.append(np.imag(trace))
		traces.append(np.absolute(trace))
		traces.append(np.angle(trace))
	drive_array = np.linspace(drive_freq, drive_freq, probe_numpoints)
	data.add_data_point(drive_array, probe_array, *traces, meta=True)

#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])