from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar
# import pandas as pd
import matplotlib.pyplot as plt
################################################
##  PARAMETERS
################################################
data_file_name = raw_input('Enter name of data file: ')

# mixer_lo_power = 7 #dBm at VNA
# measurement_power = -3 #at SMF after 60 dB attenuation

measurement_start_frequency = 7.35308*GHz#+2*MHz #dBm 60dB attenuation
measurement_stop_frequency = 7.35308*GHz#-5*MHz #dBm 60dB attenuation
measurement_frequency_numpoints = 1
measurement_frequency_array = np.linspace(measurement_start_frequency,measurement_stop_frequency,measurement_frequency_numpoints)

Number = 100
# control_frequency_start = 6.237*GHz
# control_frequency_stop = 6.237*GHz
# control_frequency_numpoints = 2
# control_frequency_array = np.linspace(control_frequency_start,control_frequency_stop,control_frequency_numpoints)
# control_frequency_array = [6.245*GHz]
# control_frequency_array = [6.25464*GHz]
# control_frequency_array = np.linspace(6.2*GHz,6.28*GHz,11)
mix_freq = 133*MHz

# lock_in_time_constant = 400*ns
# measurement_pulse_length = 4*us

# control_pulse_length_start = 100*ns
# control_pulse_length_stop = 600*ns
# control_pulse_length_numpoints = 51
# control_pulse_length_array = np.linspace(control_pulse_length_start, control_pulse_length_stop, control_pulse_length_numpoints)
# dead_time = 40*us

# channels = [1,2,3]
# volt_per_div = [10e-3, 10e-3,10e-3]
# ch_position = [0,0,0]
# time_per_div = 2*us
# resolution = 10*ns
# average_count = 10000

################################################
## SETUP
################################################

# Initialize Instruments
# uhf = ZurichInstruments_UHFLI('dev2232', reset=True) # Initializing UHFLI
znb = qt.instruments.create('ZNB20',	'RhodeSchwartz_ZNB20',		address = ZNB20_ADDRESS)
smf = qt.instruments.create('SMF100',	'RhodeSchwartz_SMF100',		address = SMF100_ADDRESS)
rte = qt.instruments.create('RTE1104',	'RhodeSchwartz_RTE1104',	address = RTE_1104_ADDRESS)
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS)

# Setup VNA as LO
# znb.set_external_reference(True)
# znb.set_external_reference_frequency(10)
# znb.set_sweep_type('cw')
# znb.set_center_frequency(measurement_frequency - mix_freq)
# znb.set_source_power(mixer_lo_power)
# znb.add_trace('S21')

# Setup SMF as measurement signal generator
# smf.set_frequency(measurement_frequency)
# smf.set_source_power(measurement_power) # dBm
# smf.pulse_mod_on()#video_polarity = 'INV')

# Setup APSYN as contol signal generator
# aps.set_external_reference()
# aps.set_frequency(control_frequency_array[0])
# aps.set_pulm_state(True)
# aps.set_pulm_source('EXT')

# Setup Lock-in initially
# uhf.extclk()
# uhf.set('oscs/0/freq', mix_freq)
# uhf.setup_demod(demod_index = 1, order = 1, timeconstant = lock_in_time_constant)
# uhf.setup_auxout(aux_index = 1, output=0, demod = 1, scale = 500)
# uhf.setup_auxout(aux_index = 2, output=1, demod = 1, scale = 500)
# uhf.setup_auxout(aux_index = 3, output=2, demod = 1, scale = 500)
# uhf.setup_auxout(aux_index = 4, output=3, demod = 1, scale = 10e-3)
# uhf.trig_out_on(1)
# uhf.trig_out_on(2, source=9)
# uhf.imp_50() #

def new_awg_program(control_pulse_length, measurement_pulse_length, dead_time):
	# Setup AWG
	control_string = 'wave m1 = marker(%d, 1);\n' % uhf.time_to_samples(control_pulse_length)
	measurement_string = 'wave m2 = marker(%d, 2);\n' % uhf.time_to_samples(measurement_pulse_length)
	# dead_string = 'wave m3 = marker(%d, 0);\n' % uhf.time_to_samples(dead_time)
	awg_program = control_string + measurement_string + \
	r"""
	wave m = join(m1,m2);

	while(true) {
		playWave(1, m);
		wait(1000000);
	}
	"""

	uhf.setup_awg(awg_program)
	uhf.awg_on(single=False)

def generate_meta_file(no, index, measurement_frequency, no_of_measurement):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (no_of_measurement, measurement_frequency, measurement_frequency_array[0], 'Frequency'))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (index, no, 0, 'Number'))
    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

# Setup Scope
# rte.set_ext_ref(True)
# rte.set_trig_source('EXT')
# rte.set_trig_level5(0.7)
# rte.set_reference_pos(0)

# for ch in channels:
# 	rte.ch_on(ch)
# 	rte.coupling_50(ch)

# rte.setup_scope(channels, volt_per_div, ch_position, time_per_div, resolution)
# rte.average_mode(True)
# rte.set_count(average_count)
channels = [1,2]
rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'
################################################
## START EXPERIMENT
################################################

# Turn on signals
# znb.rf_on()
# smf.rf_on()
# aps.rf_on()

# Initial AWG for seeing
# new_awg_program(control_pulse_length_array[0], measurement_pulse_length, dead_time)

## SETTING UP DATA FILE
data=qt.Data(name=data_file_name)
data.add_coordinate('Number', units='Hz')
data.add_coordinate('Frequency', units='Hz')
data.add_coordinate('Time', units='s')

# data.add_value('X-Quadrature')
# data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

Number_progress_bar = progressbar.ProgressBar(maxval=Number, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
Number_progress_bar.start()

# measurement_frequency_progress_bar = progressbar.ProgressBar(maxval=measurement_frequency_numpoints, \
#     widgets=['Each Tau: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
# measurement_frequency_progress_bar.start()



for index, no in enumerate(range(Number)):
	arr = np.linspace(no, no, record_length)
	for no_of_measurement, measurement_frequency in enumerate(measurement_frequency_array):
		smf.set_frequency(measurement_frequency)
		znb.set_center_frequency(measurement_frequency - mix_freq)
		znb.send_trigger()
		rte.reset_averages()
		rte.run_nx_single(wait=True)
		measurement_length_arr = np.linspace(measurement_frequency, measurement_frequency, record_length)
		time_array, voltages = rte.get_data(channels)
		# voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
		data.add_data_point(arr, measurement_length_arr, time_array, (voltages[0]**2+voltages[1]**2)**0.5)
		# measurement_frequency_progress_bar.update(no_of_measurement+1)

	generate_meta_file(no, index+1, measurement_frequency, 1)
	Number_progress_bar.update(index+1)

# df = pd.DataFrame(areas, index=control_frequency_array, columns=control_pulse_length_array)
# df.to_csv(data.get_filepath()[:-4]+'.csv')
data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
