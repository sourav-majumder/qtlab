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
	const random_phase = %f;
	const pulse_length = %f;
	const pi = 3.141592653589793;

	wave w_gauss = gauss(64, 0.2545454545454546, 32, 16);
	wave w_rise = cut(w_gauss, 0, 31);
	wave w_fall = cut(w_gauss, 32, 63);
	wave w_flat = rect(pulse_length, 1);
	wave w1 = sine(pulse_length+64, 1, random_phase + opt_phase, (pulse_length+64)*6/128);
	wave w2 = sine(pulse_length+64, 1, random_phase + 0, (pulse_length+64)*6/128);
	wave w_pulse = join(w_rise, w_flat, w_fall);
	wave t1 = multiply(w_pulse, w1);
	wave t2 = multiply(w_pulse, w2);
	wave p1 = join(t1,t1,t1,t1);
	wave p2 = join(t2,t2,t2,t2);

	wave wpiby2 = gauss(64, 0.5090909090909091, 32, 16);
	wave rx1 = multiply(wpiby2, sine(64, 1, opt_phase, 3));
	wave rx2 = multiply(wpiby2, sine(64, 1, 0, 3));

	wave ry1 = multiply(wpiby2, sine(64, 1, pi/2 + opt_phase, 3));
	wave ry2 = multiply(wpiby2, sine(64, 1, pi/2 + 0, 3));

	while (getUserReg(0) == 5) {
		playWave(zeros(1), zeros(1));
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
		wait(100*us/cycle);
	}

	//wave w_sat = rect(100*1800, 1);
	//wave w_sat_pulse = join(w_rise, w_sat, w_fall);
	//wave w_sat1 = multiply(w_sat_pulse, sine(100*1800+64, 1, opt_phase, (100*1800+64)*6/128));
	//wave w_sat2 = multiply(w_sat_pulse, sine(100*1800+64, 1, 0, (100*1800+64)*6/128));

	while (getUserReg(0) == 1) {
		wave w_sat_rise1 = multiply(w_rise, sine(32, 1, opt_phase, 1.5));
		wave w_sat_rise2 = multiply(w_rise, sine(32, 1, 0, 1.5));
		playWave(w_sat_rise1,w_sat_rise2);
		waitWave();
		var i;
		for (i=0; i<3000; i=i+1) {
			playWave(sine(64, 1, pi+opt_phase, 3), sine(64, 1, pi, 3));
			waitWave();
		}
		wave w_sat_fall1 = multiply(w_fall, sine(32, 1, pi + opt_phase, 1.5));
		wave w_sat_fall2 = multiply(w_fall, sine(32, 1, pi, 1.5));
		playWave(w_sat_fall1,w_sat_fall2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
		wait(100*us/cycle);
	}

	while (getUserReg(0) == 2) {
		playWave(p1,p2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
		wait(100*us/cycle);
	}

	while (getUserReg(0) == 3) {
		wave pl1 = join(p1, rx1);
		wave pl2 = join(p2, rx2);
		playWave(pl1,pl2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
		wait(100*us/cycle);
	}

	while (getUserReg(0) == 4) {
		wave pl1 = join(p1, ry1);
		wave pl2 = join(p2, ry2);
		playWave(pl1,pl2);
		waitWave();
		wait(6); // Unit CLK CYCLES; Added to have gap between control and measure pulses
		setTrigger(0b0010);
		wait(25*us/cycle);
		setTrigger(0b0000);
		wait(100*us/cycle);
	}'''%(rphase, rlength)
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
			(5, 5, 1, 'Tomography Step'))
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
data.add_comment('Number of points in one step is %d' % record_length)
data.add_comment('Step 1: Ground State')
data.add_comment('Step 2: Saturated')
data.add_comment('Step 3: After Process')
data.add_comment('Step 4: After pi/2 x')
data.add_comment('Step 5: After p/2 y')
# data.add_coordinate('Frequency', units = 'Hz')
data.add_coordinate('Time', units = 's')

data.add_value('X-Quadrature')
data.add_value('Y-Quadrature')
data.add_value('R-Quadrature')

#######################################################################

uhf.setup_awg(awg_program(random_length, random_phase))
uhf.awg_on(single=False)

raw_input('Turn off control')

uhf.set('awgs/0/userregs/0', 5.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(time_array, *voltages)

copy_script()
generate_meta_file()

raw_input('Turn on Control')

uhf.set('awgs/0/userregs/0', 1.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(time_array, *voltages)

uhf.set('awgs/0/userregs/0', 2.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(time_array, *voltages)


uhf.set('awgs/0/userregs/0', 3.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(time_array, *voltages)

uhf.set('awgs/0/userregs/0', 4.0)
rte.reset_averages()
rte.run_nx_single(wait=True)
time_array, voltages = rte.get_data(channels)
voltages.append((voltages[0]**2+voltages[1]**2)**0.5)
data.add_data_point(time_array, *voltages)