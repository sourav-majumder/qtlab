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
data_file_name = raw_input('Filename : ')

iq_lo_power = 7 #dBm at VNA
measurement_power = 4 #at SMF after 50 dB attenuation + 20 dB directional coupler

measurement_frequency_start = 7.84967*GHz #at SMF
measurement_frequency_stop = 7.84967*GHz #at SMF
measurement_frequency_numpoints = 1
measurement_frequency_array = np.linspace(measurement_frequency_start,measurement_frequency_stop,measurement_frequency_numpoints)


# control_frequency_start = 6.054*GHz
# control_frequency_stop = 6.054*GHz
control_frequency_start = 6.054*GHz-50*MHz
control_frequency_stop = 6.054*GHz+50*MHz
control_frequency_numpoints = 51
control_frequency_array = np.linspace(control_frequency_start,control_frequency_stop,control_frequency_numpoints)
# control_frequency_array = [6.245*GHz]
# control_frequency_array = [6.25464*GHz]
# control_frequency_array = np.linspace(6.2*GHz,6.28*GHz,11)
mix_freq = 49*MHz

lock_in_time_constant = 300*ns



channels = [1,2,3]
volt_per_div = [10e-3, 10e-3,400e-3]
ch_position = [0,0,0]
time_per_div = 5*us
resolution = 25*ns
average_count = 10000

################################################
## SETUP
################################################

# Initialize Instruments
uhf = ZurichInstruments_UHFLI('dev2232', reset=True) # Initializing UHFLI
znb = qt.instruments.create('ZNB20',	'RhodeSchwartz_ZNB20',		address = ZNB20_ADDRESS,	reset=True)
smf = qt.instruments.create('SMF100',	'RhodeSchwartz_SMF100',		address = SMF100_ADDRESS,	reset=True)
rte = qt.instruments.create('RTE1104',	'RhodeSchwartz_RTE1104',	address = RTE_1104_ADDRESS,	reset=True)
aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS,	reset=True)

# Setup VNA as control signal generator
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_sweep_type('cw')
znb.set_sweeptime(1000000)
znb.set_center_frequency(measurement_frequency_array[0] - mix_freq)
znb.set_source_power(iq_lo_power)
znb.add_trace('S21')
znb.send_trigger()

# Setup APSYN as contol signal generator
aps.set_external_reference()
aps.set_frequency(control_frequency_array[0])
aps.set_pulm_state(True)
aps.set_pulm_source('EXT')


# Setup SMF as measurement signal generator
smf.set_frequency(measurement_frequency_array[0])
smf.set_source_power(measurement_power) # dBm
smf.pulse_mod_on()#video_polarity = 'INV')


# Setup Lock-in initially
uhf.extclk()
uhf.set('oscs/0/freq', mix_freq)
uhf.set('sigins/0/ac', 1)
uhf.set('demods/0/order', 3)
uhf.setup_demod(demod_index = 1, order = 1, timeconstant = lock_in_time_constant)
uhf.setup_auxout(aux_index = 1, output=0, demod = 1, scale = 1e3)
uhf.setup_auxout(aux_index = 2, output=1, demod = 1, scale = 1e3)
uhf.setup_auxout(aux_index = 3, output=2, demod = 1, scale = 20e3)
uhf.setup_auxout(aux_index = 4, output=3, demod = 1, scale = 1)
uhf.trig_out_on(1)
uhf.imp_50() #


def generate_meta_file(no_of_control_frequency, control_frequency):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (record_length,  start_time/us, stop_time/us, 'Time(us)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (no_of_control_frequency, control_frequency, control_frequency_array[0], 'Hz'))
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
rte.set_reference_pos(30)

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
aps.rf_on()

# Initial AWG for seeing
uhf.set('sigins/0/range', 40e-3)


## SETTING UP DATA FILE
data=qt.Data(name=data_file_name)
data.add_coordinate('Frequency', units='Hz')
data.add_coordinate('Time', units='s')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')
data.add_value('R-Math')

control_frequency_progress_bar = progressbar.ProgressBar(maxval=control_frequency_numpoints, \
    widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
control_frequency_progress_bar.start()

areas = []
for no_of_control_frequency, control_frequency in enumerate(control_frequency_array):
	aps.set_frequency(control_frequency)
	rte.reset_averages()
	rte.run_nx_single(wait=True)
	control_freq_arr = np.linspace(control_frequency, control_frequency, record_length)
	time_array, voltages = rte.get_data(channels)
	voltages.append((voltages[0]**2 + voltages[1]**2)**0.5)
	data.add_data_point(control_freq_arr, time_array, *voltages)
	generate_meta_file(no_of_control_frequency+1, control_frequency)
	control_frequency_progress_bar.update(no_of_control_frequency+1)


data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
