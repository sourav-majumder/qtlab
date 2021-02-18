from constants import *
import sys
import os
import shutil
import qt
import progressbar
import time
# import pandas as pd
# import matplotlib.pyplot as plt
################################################
##  PARAMETERS
################################################
data_file_name = raw_input('Filename : ')

iq_lo_power = 7 #dBm at VNA
measurement_power = 4 #at SMF after 50 dB attenuation + 20 dB directional coupler

measurement_frequency_start = 7.84967*GHz #at SMF
measurement_frequency_stop = 7.84967*GHz #at SMF
measurement_frequency_numpoints = 1
measurement_frequency_array = np.linspace(measurement_frequency_start,measurement_frequency_stop,measurement_frequency_numpoints)


# control_frequency_start = 6.054*GHz
# control_frequency_stop = 6.054*GHz
control_frequency_start = 6.068*GHz
control_frequency_stop = 6.068*GHz
control_frequency_numpoints = 1
control_frequency_array = np.linspace(control_frequency_start,control_frequency_stop,control_frequency_numpoints)
# control_frequency_array = [6.245*GHz]
# control_frequency_array = [6.25464*GHz]
# control_frequency_array = np.linspace(6.2*GHz,6.28*GHz,11)
mix_freq = 49*MHz

lock_in_time_constant = 300*ns

delay_length_start = 0
delay_length_stop = 0
delay_length_numpoints = 100000
delay_length_array = np.linspace(delay_length_start, delay_length_stop, delay_length_numpoints)

channels = [1,2]
volt_per_div = [1, 1]
ch_position = [0,0]
time_per_div = 3*us
resolution = 10*ns
average_count = 1000

################################################
## SETUP
################################################

# Initialize Instruments
znb = qt.instruments.create('ZNB20',	'RhodeSchwartz_ZNB20',		address = ZNB20_ADDRESS,	reset=True)
smf = qt.instruments.create('SMF100',	'RhodeSchwartz_SMF100',		address = SMF100_ADDRESS,	reset=True)
rte = qt.instruments.create('RTE1104',	'RhodeSchwartz_RTE1104',	address = RTE_1104_ADDRESS,	reset=True)
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS,	reset=True)

# Setup VNA as control signal generator
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_sweep_type('cw')
znb.set_sweeptime(100000)
znb.set_center_frequency(measurement_frequency_array[0] - mix_freq)
znb.set_source_power(iq_lo_power)
znb.add_trace('S21')
znb.send_trigger()

# Setup APSYN as contol signal generator
# aps.set_external_reference()
# aps.set_frequency(control_frequency_array[0])
# aps.set_pulm_state(True)
# aps.set_pulm_source('EXT')


# Setup SMF as measurement signal generator
smf.set_frequency(measurement_frequency_array[0])
smf.set_source_power(measurement_power) # dBm
smf.pulse_mod_on()#video_polarity = 'INV')



def generate_meta_file(no_of_delay, delay):
	metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
	metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
			(record_length,  start_time/us, stop_time/us, 'Time(us)'))
	metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
			(no_of_delay, delay, delay_length_array[0], 'Sample Point'))
	metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

	metafile.write('#for each of the values\n')
	values = data.get_values()
	i=0
	while i<len(values):
		metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
		i+=1
	metafile.close()


# Setup Scope
rte.set_ext_ref(True)
rte.set_trig_source('EXT')

rte.set_trig_level5(0.7)
rte.set_reference_pos(20)

for ch in channels:
	rte.ch_on(ch)
	rte.coupling_50(ch)

rte.setup_scope(channels, volt_per_div, ch_position, time_per_div, resolution)
rte.average_mode(True)
rte.set_count(average_count)
rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'
################################################
## START EXPERIMENT
################################################

# Turn on signals
znb.rf_on()
smf.rf_on()
# aps.rf_on()



## SETTING UP DATA FILE
data=qt.Data(name=data_file_name)
data.add_coordinate('Delay length', units='Sample point')
data.add_coordinate('Time', units='s')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Math')

delay_progress_bar = progressbar.ProgressBar(maxval=delay_length_numpoints, \
	widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
delay_progress_bar.start()

areas = []
for no_of_delay, delay in enumerate(delay_length_array):
	rte.reset_averages()
	rte.run_nx_single(wait=True)
	delay_arr = np.linspace(delay, delay, record_length)
	time_array, voltages = rte.get_data(channels)
	x = voltages[0]-np.average(voltages[0][:record_length/10])
	y = voltages[1]-np.average(voltages[1][:record_length/10])
	r_values = (x**2+y**2)**0.5
	voltages.append((voltages[0]**2 + voltages[1]**2)**0.5)
	data.add_data_point(delay_arr, time_array, *voltages)
	generate_meta_file(no_of_delay+1, delay)
	delay_progress_bar.update(no_of_delay+1)


data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
