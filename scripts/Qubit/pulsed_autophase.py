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

mixer_lo_power = 7 #dBm at VNA
measurement_power = 15 #at SMF after 70 dB attenuation

measurement_frequency = 7.73508*GHz #at SMF

control_frequency_start = 6.237*GHz
control_frequency_stop = 6.237*GHz
control_frequency_numpoints = 1
control_frequency_array = np.linspace(control_frequency_start,control_frequency_stop,control_frequency_numpoints)
# control_frequency_array = [6.245*GHz]
# control_frequency_array = [6.25464*GHz]
# control_frequency_array = np.linspace(6.2*GHz,6.28*GHz,11)
mix_freq = 130*MHz

lock_in_time_constant = 400*ns
measurement_pulse_samples = 2500
# dead_time_samples = 50000

control_pulse_length_start = 180#100*ns
control_pulse_length_stop = 1000#600*ns
control_pulse_length_numpoints = 821
control_pulse_length_array = np.linspace(control_pulse_length_start, control_pulse_length_stop, control_pulse_length_numpoints)

channels = [1,2]
volt_per_div = [500e-6, 500e-6]
ch_position = [0,0]
time_per_div = 1*us
resolution = 10*ns
average_count = 100000

################################################
## SETUP
################################################

# Initialize Instruments
uhf = ZurichInstruments_UHFLI('dev2232', reset=True) # Initializing UHFLI
znb = qt.instruments.create('ZNB20',	'RhodeSchwartz_ZNB20',		address = ZNB20_ADDRESS,	reset=True)
smf = qt.instruments.create('SMF100',	'RhodeSchwartz_SMF100',		address = SMF100_ADDRESS,	reset=True)
rte = qt.instruments.create('RTE1104',	'RhodeSchwartz_RTE1104',	address = RTE_1104_ADDRESS,	reset=True)
aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS,	reset=True)

# Setup VNA as LO
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_sweep_type('cw')
znb.set_center_frequency(measurement_frequency - mix_freq)
znb.set_source_power(mixer_lo_power)
znb.add_trace('S21')

# Setup SMF as measurement signal generator
smf.set_frequency(measurement_frequency)
smf.set_source_power(measurement_power) # dBm
smf.pulse_mod_on()#video_polarity = 'INV')

# Setup Lock-in initially
uhf.extclk()
uhf.set('oscs/0/freq', mix_freq)
uhf.setup_demod(demod_index = 1, order = 1, timeconstant = lock_in_time_constant)
uhf.setup_auxout(aux_index = 1, output=0, demod = 1, scale = 750)
uhf.setup_auxout(aux_index = 2, output=1, demod = 1, scale = 750)
uhf.setup_auxout(aux_index = 3, output=2, demod = 1, scale = 1)
uhf.setup_auxout(aux_index = 4, output=3, demod = 1, scale = 10e-3)
uhf.trig_out_on(1)
uhf.trig_out_on(2, source=9)
uhf.imp_50() #

# Setup APSYN as contol signal generator
aps.set_external_reference()
aps.rf_off()
aps.set_frequency(control_frequency_array[0])
aps.set_pulm_state(True)
aps.set_pulm_source('EXT')

def new_awg_program(control_pulse_length, measurement_pulse_samples):
	# Setup AWG
	control_string = 'wave m1 = marker(%d, 1);\n' % control_pulse_length
	measurement_string = 'wave m2 = marker(%d, 2);\n' % measurement_pulse_samples
	# dead_string = 'wave m3 = marker(%d, 0);\n' % uhf.time_to_samples(dead_time)
	awg_program = control_string + measurement_string + \
	r"""
	wave m = join(m1,m2);

	while(true) {
		playWave(1, m);
		wait(50000);
	}
	"""

	uhf.setup_awg(awg_program)
	uhf.awg_on(single=False)

def generate_meta_file(control_frequency, no_of_control_frequency, control_pulse_length, no_of_control):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (no_of_control, control_pulse_length, 170, 'sample points'))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (no_of_control_frequency, control_frequency_array[0]/GHz, control_frequency/GHz, 'Frequency(GHz)'))
    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

# def autophase():
# 	smf.mod_off()
# 	uhf.set('demods/0/timeconstant', 0.3)
# 	qt.msleep(1)
	# uhf.set('/dev2232/demods/0/phaseshift', -128.420783)

# Setup Scope
rte.set_ext_ref(True)
rte.set_trig_source('EXT')
rte.set_trig_level5(0.7)
rte.set_reference_pos(0)

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

# Initial AWG for seeing
new_awg_program(control_pulse_length_array[0], measurement_pulse_samples)

## SETTING UP DATA FILE
data=qt.Data(name=data_file_name)
data.add_coordinate('Frequency', units='Hz')
data.add_coordinate('Number')
data.add_coordinate('Time', units='s')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

control_frequency_progress_bar = progressbar.ProgressBar(maxval=control_frequency_numpoints, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
control_frequency_progress_bar.start()

control_pulse_length__progress_bar = progressbar.ProgressBar(maxval=control_pulse_length_numpoints, \
    widgets=['Each Tau: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
control_pulse_length__progress_bar.start()

for no_of_control_frequency, control_frequency in enumerate(control_frequency_array):
		aps.set_frequency(control_frequency)
		control_freq_arr = np.linspace(control_frequency, control_frequency, record_length)
		for i in range(5):
			# assert raw_input('Trace Number %d:' % no_of_control).upper() != 'N'
			new_awg_program(0, measurement_pulse_samples)
			# autophase()
			rte.reset_averages()
			rte.run_nx_single(wait=True)
			control_length_arr = np.linspace(0, 0, record_length)
			time_array, voltages = rte.get_data(channels)
			voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
			data.add_data_point(control_freq_arr, control_length_arr, time_array, *voltages)
			# generate_meta_file(control_frequency, no_of_control_frequency+1, 0, i+1)

aps.rf_on()

for no_of_control_frequency, control_frequency in enumerate(control_frequency_array):
		aps.set_frequency(control_frequency)
		control_freq_arr = np.linspace(control_frequency, control_frequency, record_length)
		for i in range(5):
			# assert raw_input('Trace Number %d:' % no_of_control).upper() != 'N'
			new_awg_program(36000, measurement_pulse_samples)
			# autophase()
			rte.reset_averages()
			rte.run_nx_single(wait=True)
			control_length_arr = np.linspace(36000, 36000, record_length)
			time_array, voltages = rte.get_data(channels)
			voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
			data.add_data_point(control_freq_arr, control_length_arr, time_array, *voltages)
			# generate_meta_file(control_frequency, no_of_control_frequency+1, 36000, i+1)


try:
	# areas = []
	for no_of_control_frequency, control_frequency in enumerate(control_frequency_array):
		aps.set_frequency(control_frequency)
		control_freq_arr = np.linspace(control_frequency, control_frequency, record_length)
		# areas.append([])
		for no_of_control, control_pulse_length in enumerate(control_pulse_length_array):
			# assert raw_input('Trace Number %d:' % no_of_control).upper() != 'N'
			new_awg_program(control_pulse_length, measurement_pulse_samples)
			# autophase()
			rte.reset_averages()
			rte.run_nx_single(wait=True)
			control_length_arr = np.linspace(control_pulse_length, control_pulse_length, record_length)
			time_array, voltages = rte.get_data(channels)
			voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
			data.add_data_point(control_freq_arr, control_length_arr, time_array, *voltages)
			generate_meta_file(control_frequency, no_of_control_frequency+1, control_pulse_length, no_of_control+1+10)
			control_pulse_length__progress_bar.update(no_of_control+1)
			# areas.append(np.sum(voltages[2][np.where(time_array>1.5e-6)[0][0]:np.where(time_array<8e-6)[0][-1]]))

		control_frequency_progress_bar.update(no_of_control_frequency+1)

# df = pd.DataFrame(areas, index=control_frequency_array, columns=control_pulse_length_array)
# df.to_csv(data.get_filepath()[:-4]+'.csv')
except OSError as e:
    print 'exception thrown'
finally:
	data.close_file()
	shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
# plt.plot(areas,'.')
# plt.show()