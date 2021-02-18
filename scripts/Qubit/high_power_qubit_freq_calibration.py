import qt
import shutil
import sys
import os

from constants import *

def generate_meta_file(drive_frequency, no_of_df):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (probe_numpoints,  probe_start_power, probe_stop_power, 'Measurement Power (dBm)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (no_of_df, drive_frequency/GHz, drive_start_freq/GHz,'Frequency (GHz)'))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (1,0,1,'unused'))
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
probe_start_power = -50
probe_stop_power = -30
probe_numpoints = 1001
if_bw = 1*kHz
probe_frequency = 7.72395*GHz
averages = 20
s_params = ['S21']
filename = raw_input('File name: ')

# APSYN sweep parameters
drive_start_freq = 6.2373*GHz
drive_stop_freq = 6.2373*GHz
resolution = 100*MHz
drive_numpoints = int(abs(drive_stop_freq - drive_start_freq)/resolution + 1)

#############################
# Initialize Instruments
#############################
znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS, reset=True)
aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS,	reset=True)


# Setup VNA as source
# znb.set_external_reference(True)
# znb.set_external_reference_frequency(10)
# znb.set_source_power(probe_power)
znb.set_sweep_type('pow')
znb_isnt = znb.get_instrument()
znb_isnt.write('FREQ:FIX %E' % probe_frequency)
znb.set_start_power(probe_start_power)
znb.set_stop_power(probe_stop_power)
znb.set_numpoints(probe_numpoints)
znb.set_if_bandwidth(if_bw)
znb.set_averages(averages)
for s_param in s_params:
		znb.add_trace(s_param)

# Turn on sources
znb.rf_on()
aps.rf_on()

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
probe_array = np.linspace(probe_start_power, probe_stop_power, probe_numpoints)
znb.set_sweeps(averages)

qt.mstart()

for no_of_df, drive_freq in enumerate(drive_freq_array):
	aps.set_frequency(drive_freq)
	znb.reset_averages()
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
	generate_meta_file(drive_freq, no_of_df)

#create script in data directory
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(filename)+11)],os.path.basename(sys.argv[0])))
# copy_script(sys.argv[0], filename)
data.close_file(sys.argv[0])