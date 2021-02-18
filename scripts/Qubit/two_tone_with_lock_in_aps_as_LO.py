from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import time
import progressbar

def generate_meta_file(control_power, no_of_mp):
    metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
            (control_frequency_numpoints,  control_frequency_start/GHz, control_frequency_stop/GHz, 'Frequency(GHz)'))
    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
            (no_of_mp, control_power, control_power_start,'Power(dBm)'))
    metafile.write('#outermost loop\n%s\n%s\n%s\n%s\n'%
            (1,0,1,'unused'))
    metafile.write('#for each of the values\n')
    values = data.get_values()
    i=0
    while i<len(values):
        metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
        i+=1
    metafile.close()

################################################
##  PARAMETERS
################################################
data_file_name = raw_input('Enter name of lock_in_data file: ')

# mixer_lo_power = 7 #dBm at APS
control_power_start = 18 # with 40 dB attenuation after SMF
control_power_stop = -12
control_power_numpoints = 11
control_power_array = np.linspace(control_power_start, control_power_stop, control_power_numpoints)


control_frequency_start = 5.8*GHz
control_frequency_stop = 6.2*GHz
control_frequency_numpoints = 401
control_frequency_array = np.linspace(control_frequency_start,control_frequency_stop,control_frequency_numpoints)

measurement_frequency = 7.84967*GHz #at VNA
measurement_power = -18  #at VNA

mix_freq = 37*MHz

lock_in_time_constant = 5e-6

################################################
## SETUP
################################################

uhf = ZurichInstruments_UHFLI('dev2232', reset=True) # Initializing UHFLI
aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS,	reset=True)
znb = qt.instruments.create('ZNB20',	'RhodeSchwartz_ZNB20',		address = ZNB20_ADDRESS,	reset=True)
smf = qt.instruments.create('SMF100',	'RhodeSchwartz_SMF100',		address = SMF100_ADDRESS,	reset=True)

# Setup VNA as Measurement
znb.set_external_reference(True)
znb.set_external_reference_frequency(10)
znb.set_sweep_type('cw')
znb.set_sweeptime(100000)
znb.set_center_frequency(measurement_frequency)
znb.set_source_power(measurement_power)
znb.add_trace('S21')

# Setup SMF as measurement signal generator
smf.set_frequency(control_frequency_array[0])
smf.set_source_power(control_power_array[0]) # dBm
# smf.pulse_mod_on(video_polarity = 'INV')

# Setup APSYN as contol signal generator
aps.set_external_reference()
aps.set_frequency(measurement_frequency - mix_freq)
# aps.set_pulm_state(True)
# aps.set_pulm_source('EXT')

# Setup Lock-in initially
uhf.extclk()
uhf.set('oscs/0/freq', mix_freq)
uhf.setup_demod(demod_index = 1, order = 1, timeconstant = lock_in_time_constant, data_transfer=True, rate=1e3)
# uhf.setup_auxout(aux_index = 1, output=0, demod = 1, scale = 1000)
# uhf.setup_auxout(aux_index = 2, output=1, demod = 1, scale = 1000)
# uhf.setup_auxout(aux_index = 3, output=2, demod = 1, scale = 1)
# uhf.setup_auxout(aux_index = 4, output=3, demod = 1, scale = 10e-3)
# uhf.trig_out_on(1)
# uhf.trig_out_on(2, source=9)
uhf.imp_50()
assert raw_input('continue? [y/n]').upper() != 'N'
uhf.daq.unsubscribe('*')

time.sleep(10*lock_in_time_constant)
uhf.daq.sync()
path = '/%s/demods/0/sample' % (uhf.device_id[1:-1])

data=qt.Data(name=data_file_name)
data.add_coordinate('Power', units='dBm')
data.add_coordinate('Frequency', units='Hz')
# data.add_value('X-Quadrature')
# data.add_value('Y-Quadrature')
data.add_value('R')
# data.add_value('Phi')

aps.rf_on()
smf.rf_on()
znb.rf_on()

progress_bar = progressbar.ProgressBar(maxval=control_power_numpoints*control_frequency_numpoints, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
progress_bar.start()

index = 0
for no_of_mp,control_power in enumerate(control_power_array):
	smf.set_source_power(control_power)
	for control_frequency in control_frequency_array:
		smf.set_frequency(control_frequency)
		uhf.daq.subscribe(path)
		uhf.daq.sync()
		sleep_length = lock_in_time_constant
		time.sleep(sleep_length)
		poll_length = 1  # [s]
		poll_timeout = 1000  # [ms]
		poll_flags = 0
		poll_return_flat_dict = True
		lock_in_data = uhf.daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)
		uhf.daq.unsubscribe('*')
		assert lock_in_data, "poll() returned an empty lock_in_data dictionary, did you subscribe to any paths?"
		assert path in lock_in_data, "The lock_in_data dictionary returned by poll has no key `%s`." % path
		sample = lock_in_data[path]
		# Let's check how many seconds of demodulator lock_in_data were returned by poll.
		# First, get the sampling rate of the device's ADCs, the device clockbase...
		clockbase = float(uhf.daq.getInt('/dev2232/clockbase'))
		# ... and use it to convert sample timestamp ticks to seconds:
		dt_seconds = (sample['timestamp'][-1] - sample['timestamp'][0])/clockbase
		# print("poll() returned {:.3f} seconds of demodulator lock_in_data.".format(dt_seconds))
		tol_percent = 10
		dt_seconds_expected = sleep_length + poll_length
		assert (dt_seconds - dt_seconds_expected)/dt_seconds_expected*100 < tol_percent, \
		    "Duration of demod lock_in_data returned by poll() (%.3f s) differs " % dt_seconds + \
		    "from the expected duration (%.3f s) by more than %0.2f %%." % \
		    (dt_seconds_expected, tol_percent)

		# Calculate the demodulator's magnitude and phase and add them to the dict.
		sample['R'] = np.abs(sample['x'] + 1j*sample['y'])
		sample['phi'] = np.angle(sample['x'] + 1j*sample['y'])
		# print("Average measured RMS amplitude is {:.3e} V.".format(np.mean(sample['R'])))
		data.add_data_point(control_power, control_frequency,np.mean(sample['R']))
		index +=1
		progress_bar.update(index)
	generate_meta_file(control_power, no_of_mp+1)

data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
aps.rf_off()
smf.rf_off()
znb.rf_off()