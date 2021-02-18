from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time

# uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS)


# center_freq = 7.82067* GHz
# span = 70*MHz
# fsv.set_centerfrequencyc(enter_freq)
# fsv.set_span(span)
# fsv.set_bandwidth(10*Hz)

delay_length_start = 0
delay_length_stop = 0
delay_length_numpoints = 10
delay_length_array = np.linspace(delay_length_start, delay_length_stop, delay_length_numpoints)

control_start = 5.07*GHz
control_stop = 5.25*GHz
control_numpoints = 60
control_array = np.linspace(control_start, control_stop, control_numpoints)

# smf.set_source_control(control_array[0])


def generate_meta_file(no_of_control, control):
	metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
	metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
			(record_length,  start_time/us, stop_time/us, 'Time(us)'))
	metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
			(no_of_control, control, control_array[0], 'control'))
	metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

	metafile.write('#for each of the values\n')
	values = data.get_values()
	i=0
	while i<len(values):
		metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
		i+=1
	metafile.close()


def awg_program(control_pulse, delay = 0, measurement_pulse = 10):
	awg_program_string = """
	const fs=225;
	const us=1e-6;
	const cycle=4.4e-9;

	while (true) {
		setTrigger(0b0001); // Set control ON
		wait(%f*us/cycle); // Length of control pulse
		setTrigger(0b0000); // BOTH pulses off
		wait(%f*us/cycle);   // time between control and measure
		setTrigger(0b0010); // Enable measure pulse
		wait(%f*us/cycle);   // Length of measure pulse
		setTrigger(0b0000); // END of measure pulse
		wait(2000*us/cycle);   // Post measure wait time
	}
	
	""" % (control_pulse, delay, measurement_pulse)
	return awg_program_string
# uhf.set('awgs/0/enable', 0)
# uhf.setup_awg(awg_program(control_array[0]))
# uhf.awg_on(single=False)
# daq.setInt('/dev2232/awgs/0/enable', 1)

us = 1e-6

data_file_name = raw_input('Enter name of data file: ')

data=qt.Data(name=data_file_name)
data.add_coordinate('Number')
data.add_coordinate('Time', units='s')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

channels = [1,2]
aps.set_frequency(control_array[0])

start = time.time()

rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'

control_progress_bar = progressbar.ProgressBar(maxval=control_numpoints, \
	widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
control_progress_bar.start()

# areas = open('%s_areas'%)

for no_of_control, control in enumerate(control_array):
	# smf.mod_on()
	# uhf.setup_awg(awg_program(control))
	# uhf.awg_on(single=False)
	aps.set_frequency(control)
	rte.reset_averages()
	rte.run_nx_single(wait=True)
	control_arr = np.linspace(control, control, record_length)
	time_array, voltages = rte.get_data(channels)
	voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
	data.add_data_point(control_arr, time_array, *voltages)
	# smf.mod_off()
	# qt.msleep(8)
	# fsv.marker_to_max()
	# freq, control = fsv.get_max_freqs(1)
	# print(freq, control)
	generate_meta_file(no_of_control+1, control)
	control_progress_bar.update(no_of_control+1)


data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
print(time.time()-start)
