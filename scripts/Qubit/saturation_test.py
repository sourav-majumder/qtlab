from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import sys
import os
import shutil
import qt
import progressbar
import numpy as np
import time

def awg_program(rlength, rphase):
	awg_program = '''
	const us = 1e-6;
	const cycle = 4.4e-9;
	const opt_phase = -1.710238;
	const pi = 3.141592653589793;

	wave w_gauss = gauss(64, 1, 32, 16);
	wave w_rise = cut(w_gauss, 0, 31);
	wave w_fall = cut(w_gauss, 32, 63);
	wave w_sat_rise1 = multiply(w_rise, sine(32, 1, opt_phase, 1.5));
	wave w_sat_rise2 = multiply(w_rise, sine(32, 1, 0, 1.5));
	wave p1 = sine(64, 1, pi+opt_phase, 3);
	wave p2 = sine(64, 1, pi, 3);
	wave w_sat_fall1 = multiply(w_fall, sine(32, 1, pi + opt_phase, 1.5));
	wave w_sat_fall2 = multiply(w_fall, sine(32, 1, pi, 1.5));
	waitWave();
	var i;

	while (getUserReg(0) == 1) {
		playWave(w_sat_rise1,w_sat_rise2);
		waitWave();
		for (i=0; i<4000; i=i+1) {
			playWave(sine(64, 1, pi+opt_phase, 3), sine(64, 1, pi, 3));
			waitWave();
		}
		playWave(w_sat_fall1,w_sat_fall2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
	}

	while (getUserReg(0) == 2) {
		playWave(w_sat_rise1,w_sat_rise2);
		waitWave();
		for (i=0; i<5000; i=i+1) {
			playWave(sine(64, 1, pi+opt_phase, 3), sine(64, 1, pi, 3));
			waitWave();
		}
		playWave(w_sat_fall1,w_sat_fall2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
	}

	while (getUserReg(0) == 3) {
		playWave(w_sat_rise1,w_sat_rise2);
		waitWave();
		for (i=0; i<6000; i=i+1) {
			playWave(sine(64, 1, pi+opt_phase, 3), sine(64, 1, pi, 3));
			waitWave();
		}
		playWave(w_sat_fall1,w_sat_fall2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
	}

	while (getUserReg(0) == 4) {
		playWave(w_sat_rise1,w_sat_rise2);
		waitWave();
		for (i=0; i<7000; i=i+1) {
			playWave(sine(64, 1, pi+opt_phase, 3), sine(64, 1, pi, 3));
			waitWave();
		}
		playWave(w_sat_fall1,w_sat_fall2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
	}

	while (getUserReg(0) == 5) {
		playWave(w_sat_rise1,w_sat_rise2);
		waitWave();
		for (i=0; i<8000; i=i+1) {
			playWave(sine(64, 1, pi+opt_phase, 3), sine(64, 1, pi, 3));
			waitWave();
		}
		playWave(w_sat_fall1,w_sat_fall2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
	}

	while (getUserReg(0) == 6) {
		playWave(w_sat_rise1,w_sat_rise2);
		waitWave();
		for (i=0; i<9000; i=i+1) {
			playWave(sine(64, 1, pi+opt_phase, 3), sine(64, 1, pi, 3));
			waitWave();
		}
		playWave(w_sat_fall1,w_sat_fall2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
	}'''
	return awg_program

##############################################

uhf = ZurichInstruments_UHFLI('dev2232')
rte = qt.instruments.create('RTE1104', 'RhodeSchwartz_RTE1104', address = 'TCPIP0::192.168.1.6::INSTR')
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
# smf = qt.instruments.create('SMF100', 'RhodeSchwartz_SMF100', address = SMF100_ADDRESS)
# aps = qt.instruments.create('APSYN420',   'AnaPico_APSYN420',         address = APSYN420_ADDRESS)
# znb = qt.instruments.create('ZNB20', 'RhodeSchwartz_ZNB20', address=ZNB20_ADDRESS)

##############################################

def generate_meta_file():
	metafile = open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
	metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
			(record_length,  start_time/us, stop_time/us, 'Time(us)'))
	metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
			(6, 9000*64/1.8e3, 4000*64/1.8e3, 'Saturation Pulse Length (us)'))
	metafile.write('#outermost loop\n1\n0\n1\nNothing\n')

	metafile.write('#for each of the values\n')
	values = data.get_values()
	i=0
	while i<len(values):
		metafile.write('%d\n%s\n'% (i+4, values[i]['name']))
		i+=1
	metafile.close()
##################################################
def copy_script():
	shutil.copy2('%s'%sys.argv[0],'%s/%s'%(data.get_filepath()[:-(len(data_file_name)+11)],os.path.basename(sys.argv[0])))

###################################################################
#############  RUN once to setup the innermost loop

channels = [1,2]
start = time.time()
# rte.wait_till_complete()
start_time, stop_time, record_length = rte.get_header()
assert raw_input('continue? [y/n]').upper() != 'N'

####################################################################

data_file_name = raw_input('Enter name of data file: ')
random_phase = float(raw_input('Enter the random phase : '))
random_length = float(raw_input('Enter the random length : '))

data=qt.Data(name=data_file_name)
data.add_coordinate('Saturation Pulse length (samples)')
data.add_coordinate('Time', units = 's')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

#######################################################################

uhf.setup_awg(awg_program(random_length, random_phase))
uhf.awg_on(single=False)

uhf.set('awgs/0/userregs/0', 1.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(np.repeat(4000, record_length), time_array, *voltages)

copy_script()
generate_meta_file()

uhf.set('awgs/0/userregs/0', 2.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(np.repeat(5000, record_length), time_array, *voltages)

uhf.set('awgs/0/userregs/0', 3.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(np.repeat(6000, record_length), time_array, *voltages)


uhf.set('awgs/0/userregs/0', 4.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(np.repeat(7000, record_length), time_array, *voltages)

uhf.set('awgs/0/userregs/0', 5.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(np.repeat(8000, record_length), time_array, *voltages)

uhf.set('awgs/0/userregs/0', 6.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(np.repeat(9000, record_length), time_array, *voltages)