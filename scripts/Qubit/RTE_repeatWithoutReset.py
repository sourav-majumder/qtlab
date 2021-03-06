from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time

uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',			address = APSYN420_ADDRESS)


# center_freq = 7.82067* GHz
# span = 70*MHz
# fsv.set_centerfrequencyc(enter_freq)
# fsv.set_span(span)
# fsv.set_bandwidth(10*Hz)

delay_length_start = 0
delay_length_stop = 0
delay_length_numpoints = 10
delay_length_array = np.linspace(delay_length_start, delay_length_stop, delay_length_numpoints)

control_start = 5.6365*GHz - 20*MHz
control_stop = 5.6365*GHz + 20*MHz
# control_start = 5.6*GHz
# control_stop = 5.68*GHz
control_numpoints = 11
control_array = np.linspace(control_start, control_stop, control_numpoints)

power_start = 0
power_stop = 200 #at SA -36.35 dBm, after 4dB cable and 20dB directional coupler
power_inc = 3
power_array = np.arange(power_start,power_stop,power_inc)
power_numpoints = len(power_array)
# power_array = np.linspace(power_start, power_stop, power_numpoints)

gauss_width = 32 #in sample points


pulse_start = 0
pulse_stop = 200
pulse_inc = 16
pulse_array = np.arange(pulse_start,pulse_stop,pulse_inc)
pulse_numpoints = len(pulse_array)#int((pulse_stop-pulse_start)/pulse_inc)
# pulse_array = np.linspace(pulse_start, pulse_stop, pulse_numpoints+1)


def generate_meta_file(no_of_power, power):
	metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
	metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
			(record_length,  start_time/us, stop_time/us, 'Time(us)'))
	metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
			(no_of_power, power, power_array[0], 'Power(mV)'))
	metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')

	metafile.write('#for each of the values\n')
	values = data.get_values()
	i=0
	while i<len(values):
		metafile.write('%d\n%s\n'% (i+3, values[i]['name']))
		i+=1
	metafile.close()


def awg_program(power_points, pulse_length=pulse_array[0], sigma=gauss_width):
	awg_program_string = """
	const marker_pos = 0;
	const cycle = 4.4e-9;
	const us = 1e-6;
	const pulse_length = %f;
	const power = %f;
	const sigma = %f;
	wave trig = marker(7*1800, 2);
	wave w_gauss= gauss(4*sigma, power/750, 2*sigma, sigma);
	wave w_rise = cut(w_gauss, 0, 2*sigma-1);
	wave w_fall = cut(w_gauss, 2*sigma, 4*sigma-1);
	wave w_flat = rect(pulse_length, power/750);
	wave w_pulse = join(zeros(8), w_rise, w_flat, w_fall, zeros(8), trig);
	wave w_pulse2 = w_pulse;
	while (true) {
	playWave(w_pulse,w_pulse2);
	wait(150*us/cycle);
	}
	""" % (pulse_length,power_points,sigma)
	return awg_program_string
# uhf.set('awgs/0/enable', 0)
uhf.setup_awg(awg_program(pulse_array[0]))
uhf.awg_on(single=False)
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
# aps.set_frequency(control_array[0])

start = time.time()

rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'

power_progress_bar = progressbar.ProgressBar(maxval=power_numpoints, \
	widgets=['Total: ', progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
power_progress_bar.start()


for no_of_power, power in enumerate(power_array):
	uhf.setup_awg(awg_program(power))
	uhf.awg_on(single=False)
	# aps.set_frequency(control)
	rte.reset_averages()
	rte.run_nx_single(wait=True)
	power_arr = np.linspace(power, power, record_length)
	time_array, voltages = rte.get_data(channels)
	voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
	data.add_data_point(power_arr, time_array, *voltages)
	generate_meta_file(no_of_power+1, power)
	power_progress_bar.update(no_of_power+1)


data.close_file()
shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))
print(time.time()-start)
