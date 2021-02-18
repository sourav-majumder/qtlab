from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar

################################################
##  PARAMETERS
################################################
data_file_name = raw_input('Enter name of data file: ')

mixer_lo_power = 7 #dBm at VNA
measurement_power = 1 #at SMF after 70 dB attenuation

measurement_frequency = 7.84967*GHz #at SMF

control_frequency = 6.068*GHz
mix_freq = 37*MHz

lock_in_time_constant = 600*ns
measurement_pulse_samples = 225*12

control_pulse_length = 225*100

gap_length_numpoints = 31
gap_length_array = np.linspace(0, 15*225, gap_length_numpoints)

channels = [1,2]
volt_per_div = [1, 1]
ch_position = [0,0]
time_per_div = 4*us
resolution = 10*ns
average_count = 100000

################################################
## SETUP
################################################
# Initialize Instruments
uhf = ZurichInstruments_UHFLI('dev2232') # Initializing UHFLI
# znb = qt.instruments.create('ZNB20',	'RhodeSchwartz_ZNB20',		address = ZNB20_ADDRESS)
smf = qt.instruments.create('SMF100',	'RhodeSchwartz_SMF100',		address = SMF100_ADDRESS)
rte = qt.instruments.create('RTE1104',	'RhodeSchwartz_RTE1104',	address = RTE_1104_ADDRESS)
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS)

# Setup VNA as LO
# znb.set_external_reference(True)
# znb.set_external_reference_frequency(10)
# znb.set_sweep_type('cw')
# znb.set_sweeptime(100000)
# znb.set_center_frequency(measurement_frequency + mix_freq)
# znb.set_source_power(mixer_lo_power)
# znb.add_trace('S21')

# Setup SMF as measurement signal generator
smf.set_frequency(measurement_frequency)
smf.set_source_power(measurement_power) # dBm
smf.pulse_mod_on()#video_polarity = 'INV')

# Setup Lock-in initially
# uhf.extclk()
# uhf.set('oscs/0/freq', mix_freq)
# uhf.setup_demod(demod_index = 1, order = 1, timeconstant = lock_in_time_constant)
# uhf.setup_auxout(aux_index = 1, output=0, demod = 1, scale = 750)
# uhf.setup_auxout(aux_index = 2, output=1, demod = 1, scale = 750)
# uhf.setup_auxout(aux_index = 3, output=2, demod = 1, scale = 1)
# uhf.setup_auxout(aux_index = 4, output=3, demod = 1, scale = 10e-3)
uhf.trig_out_on(1)
# uhf.trig_out_on(2, source=9)
uhf.imp_50()

# # Setup APSYN as contol signal generator
# aps.set_external_reference()
# aps.rf_off()
# aps.set_frequency(control_frequency)
# aps.set_pulm_state(True)
# aps.set_pulm_source('EXT')

def new_awg_program(gap):
	# Setup AWG
	control_string = 'wave m1 = marker(%d, 1);\n' % control_pulse_length
	gap_string = 'wave m2 = marker(%d, 0);\n' % int(gap)
	measurement_string = 'wave m3 = marker(%d, 2);\n' % measurement_pulse_samples
	# dead_string = 'wave m3 = marker(%d, 0);\n' % uhf.time_to_samples(dead_time)
	awg_program = control_string + gap_string + measurement_string + \
	r"""
	wave m = join(m1,m2,m3);

	while(true) {
		playWave(1, m);
		wait(200000);
	}
	"""

	uhf.setup_awg(awg_program)
	uhf.awg_on(single=False)

def generate_meta_file(gap, no_of_gap):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (no_of_gap, gap, gap_length_array[0], 'sample points'))
    metafile.write('#outermost loop\n1\n0\n1\nNothing\n')
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
rte.set_reference_pos(10)

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
# znb.rf_on()
smf.rf_on()
# aps.rf_on()

# Initial AWG for seeing
new_awg_program(0)

## SETTING UP DATA FILE
data=qt.Data(name=data_file_name)
data.add_coordinate('Gap')
data.add_coordinate('Time', units='s')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Math')
# data.add_comment('Control Frequency: %f GHz, Control pulse length: %d samples' % (control_frequency/GHz, control_pulse_length))

gap_length_progress_bar = progressbar.ProgressBar(maxval=gap_length_numpoints, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
gap_length_progress_bar.start()


for no_of_gap, gap in enumerate(gap_length_array):
	new_awg_program(gap)
	rte.reset_averages()
	rte.run_nx_single(wait=True)
	gap_arr = np.linspace(gap, gap, record_length)
	time_array, voltages = rte.get_data(channels)
	voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
	data.add_data_point(gap_arr, time_array, *voltages)
	generate_meta_file(gap, no_of_gap+1)
	gap_length_progress_bar.update(no_of_gap+1)

data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
