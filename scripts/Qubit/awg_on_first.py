import qt
from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import numpy as np
import matplotlib.pyplot as plt
import time
import progressbar

center_freq = None
mix_freq = None
sideband = None
# aps = qt.instruments.create('APSYN420',	'AnaPico_APSYN420',	address = APSYN420_ADDRESS)
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
uhf = ZurichInstruments_UHFLI('dev2232') # Initializing UHFLI

def get_power():
	_ , power = fsv.get_max_freqs(1)
	return power[0]

def sideband_diff(sideband = 'right12'):
	qt.msleep(0.1)
	freqs, powers = fsv.get_max_freqs(2)
	while (abs(freqs[0]-freqs[1]) < mix_freq*2-2*MHz or abs(freqs[0]-freqs[1]) > mix_freq*2+2*MHz):
		fsv.marker_next(2)
		freqs, powers = fsv.get_max_freqs(2)
	powers = [power for _,power in sorted(zip(freqs,powers))]
	if sideband is 'right':
		return powers[-1]-powers[0]
	else:
		return powers[0]-powers[-1]

def dc_sweep(i_arr, q_arr, plot = False):
	uhf.set('sigouts/0/offset', 0.0)
	uhf.set('sigouts/1/offset', 0.0)
	import progressbar
	progress_bar = progressbar.ProgressBar(maxval=len(i_arr), \
	    widgets=['Optimizing DC Offsets: ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
	progress_bar.start()
	pow_arr = []
	for index, i in enumerate(i_arr):
		uhf.set('sigouts/0/offset', i)
		pow_arr.append([])
		progress_bar.update(index+1)
		for q in q_arr:
			uhf.set('sigouts/1/offset', q)
			pow_arr[-1].append(get_power())
	progress_bar.finish()
	pow_arr = np.array(pow_arr)
	indices = np.where(pow_arr == pow_arr.min())
	uhf.set('sigouts/0/offset', i_arr[indices[0][0]])
	uhf.set('sigouts/1/offset', q_arr[indices[1][0]])
	if plot:
		plt.imshow(pow_arr, aspect='auto', extent=[q_arr[0], q_arr[-1], i_arr[-1], i_arr[-0]])
		plt.show()
	return i_arr[indices[0][0]],q_arr[indices[1][0]]

def optimize_dc(plot = False):
	fsv.set_centerfrequency(center_freq)
	fsv.set_span(2*MHz)
	fsv.set_bandwidth(10*kHz)
	fsv.set_sweep_points(3001)
	uhf.set('sigouts/0/offset', 0.0)
	uhf.set('sigouts/1/offset', 0.0)
	qt.msleep(1)
	fsv.marker_to_max()
	freq, power = fsv.get_max_freqs(1)


	i_arr = np.linspace(-750e-3, 750e-3, 50) # -18.49m
	q_arr = np.linspace(-750e-3, 750e-3, 50) # -24.24m
	opt_i, opt_q = dc_sweep(i_arr, q_arr, plot)
	# Coarse sweep
	i_arr = np.linspace(opt_i-30e-3, opt_i+30e-3, 10)
	q_arr = np.linspace(opt_q-30e-3, opt_q+30e-3, 10)
	opt_i, opt_q = dc_sweep(i_arr, q_arr, plot)
	# Fine sweep
	i_arr = np.linspace(opt_i-1e-3, opt_i+1e-3, 10)
	q_arr = np.linspace(opt_q-1e-3, opt_q+1e-3, 10)
	opt_i, opt_q = dc_sweep(i_arr, q_arr, plot)
	# Finer sweep
	i_arr = np.linspace(opt_i-0.5e-3, opt_i+0.5e-3, 20)
	q_arr = np.linspace(opt_q-0.5e-3, opt_q+0.5e-3, 20)
	return dc_sweep(i_arr, q_arr, plot)

def optimize_ph(ph_arr=np.linspace(-180, 180, 720), plot = False):
	# uhf.set('sigouts/1/amplitudes/7', 700e-3)
	# uhf.set('sigouts/0/amplitudes/3', 700e-3)
	# uhf.set('demods/3/phaseshift', 0)
	diffs = []
	import progressbar
	progress_bar = progressbar.ProgressBar(maxval=len(ph_arr), \
	    widgets=['Optimizing Phase ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
	progress_bar.start()
	for index, phase in enumerate(ph_arr):
		# uhf.set('demods/3/phaseshift', phase)
		uhf.setup_awg(awg_program(phase))
		uhf.awg_on(single=False)
		qt.msleep(1)
		fsv.markers_to_peaks(2)
		diffs.append(sideband_diff())
		progress_bar.update(index+1)
	progress_bar.finish()
	diffs = np.array(diffs)
	indices = np.where(diffs == diffs.max())
	# uhf.set('demods/3/phaseshift', ph_arr[indices[0][0]])
	uhf.setup_awg(awg_program(ph_arr[indices[0][0]]))
	uhf.awg_on(single=False)
	if plot:
		plt.plot(ph_arr, diffs)
		plt.show()
	return ph_arr[indices[0][0]]

def optimize_phase(plot=False):
	ph_arr = np.linspace(-np.pi, np.pi, 20)
	opt_ph = optimize_ph(ph_arr, plot)
	# Fine sweep
	ph_arr = np.linspace(opt_ph-0.314, opt_ph+0.314, 20)
	opt_ph = optimize_ph(ph_arr, plot)
	# Finer sweep
	ph_arr = np.linspace(opt_ph-0.015, opt_ph+0.015, 20)
	return optimize_ph(ph_arr, plot)

def optimize_amp(i_arr, q_arr, plot=False):
	diffs = []
	import progressbar
	progress_bar = progressbar.ProgressBar(maxval=len(i_arr), \
	    widgets=['Optimizing Amplitude', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
	progress_bar.start()
	for index, i in enumerate(i_arr):
		uhf.set('awgs/0/outputs/0/amplitude', i)
		# uhf.set('sigouts/0/amplitudes/3', i)
		diffs.append([])
		progress_bar.update(index+1)
		for q in q_arr:
			uhf.set('awgs/0/outputs/1/amplitude', q)
			# uhf.set('sigouts/1/amplitudes/7', q)
			diffs[-1].append(sideband_diff())
	progress_bar.finish()
	diffs = np.array(diffs)
	indices = np.where(diffs == diffs.max())
	uhf.set('sigouts/0/amplitudes/3', i_arr[indices[0][0]])
	uhf.set('sigouts/1/amplitudes/7', q_arr[indices[1][0]])
	if plot:
		plt.imshow(diffs, aspect='auto', extent=[q_arr[0], q_arr[-1], i_arr[-1], i_arr[-0]])
		plt.show()
	return i_arr[indices[0][0]],q_arr[indices[1][0]]

def optimize_amplitude(i_dc, q_dc, plot=False):
	i_arr = np.linspace(0, 740e-3-abs(i_dc), 10)/750e-3
	q_arr = np.linspace(0, 740e-3-abs(q_dc), 10)/750e-3
	opt_i, opt_q = optimize_amp(i_arr, q_arr, plot)
	# Fine sweep
	i_arr = (np.linspace(opt_i-10e-3/750e-3, opt_i+10e-3/750e-3, 20)).clip(0,700e-3/750e-3)
	q_arr = (np.linspace(opt_q-10e-3/750e-3, opt_q+10e-3/750e-3, 20)).clip(0,700e-3/750e-3)
	opt_i, opt_q = optimize_amp(i_arr, q_arr, plot)
	# Finer sweep
	i_arr = (np.linspace(opt_i-0.5e-3/750e-3, opt_i+0.5e-3/750e-3, 20)).clip(0,700e-3/750e-3)
	q_arr = (np.linspace(opt_q-0.5e-3/750e-3, opt_q+0.5e-3/750e-3, 20)).clip(0,700e-3/750e-3)
	return optimize_amp(i_arr, q_arr, plot)

def set_device_settings(number):
	if number == 1:
		# uhf.extclk()
		# aps.set_external_reference()
		# aps.set_frequency(center_freq)
		# aps.rf_on()
		# uhf.set('oscs/0/freq', mix_freq)
		# uhf.set('oscs/1/freq', mix_freq)
		uhf.set('awgs/0/enable', 0)
		uhf.set('sigouts/0/on', 1)
		uhf.set('sigouts/1/on', 1)
		uhf.set('sigouts/0/enables/3', 0)
		uhf.set('sigouts/1/enables/7', 0)
		uhf.imp_50()

	elif number == 2:
		uhf.set('sigouts/0/enables/3', 1)
		uhf.set('sigouts/1/enables/7', 1)
		# uhf.set('sigouts/1/amplitudes/7', 700e-3)
		# uhf.set('sigouts/0/amplitudes/3', 700e-3)
		uhf.set('awgs/0/outputs/0/amplitude', 700e-3/750e-3)
		uhf.set('awgs/0/outputs/1/amplitude', 700e-3/750e-3)
		fsv.set_span(2*mix_freq + 20*MHz)
		fsv.set_bandwidth(5*kHz)
		fsv.set_sweep_points(20001)
		qt.msleep(1)
		fsv.markers_to_peaks(2)
		uhf.awg_on(single=False)

def optimize_all(plot=False):
	uhf.setup_awg(awg_program())
	set_device_settings(1)
	i_dc, q_dc = optimize_dc(plot=plot)
	set_device_settings(2)
	# phase = -1.707080
	# uhf.setup_awg(awg_program(phase))
	# uhf.awg_on(single=False)
	phase = optimize_phase(plot=plot)
	i_amp, q_amp = optimize_amplitude(i_dc, q_dc, plot=plot)
	freqs, powers = fsv.get_max_freqs(2)
	with open('Qubit/optimize_data.txt', 'a') as file:
		file.write('\n%f %f %f %f %f %f %f %f:%f %f:%f'%(center_freq, mix_freq, i_dc, q_dc, phase, i_amp, q_amp, freqs[0], powers[0], freqs[1], powers[1]))
	return i_dc, q_dc, phase, i_amp, q_amp

def awg_program(phase=0):
	awg_program_string = """
	//sine(samples, amplitude, phaseOffset, nrOfPeriods)
	wave w2 = sine(128, 1, %f, 12);
	wave w3 = sine(128, 1, 0, 12);	
	while (true) {
	  playWave(w2, w3);
	}""" % \
	(phase)
	return awg_program_string

	# opt_i, opt_q = 0.69271052631578955, 0.6287748538011696




# freq, _ = fsv.get_data()
# traces = []
# i_arr = np.linspace(0, 700e-3, 100)
# uhf.set('sigouts/1/amplitudes/7', 0)
# for i in i_arr:
# 	uhf.set('sigouts/0/amplitudes/3', i)
# 	_ , data = fsv.get_data()
# 	traces.append(data)

# traces = np.array(traces)
# plt.imshow(traces, aspect = 'auto')
# plt.show()

# traces = []
# q_arr = np.linspace(0, 700e-3, 100)
# uhf.set('sigouts/0/amplitudes/3', 0)
# for q in q_arr:
# 	uhf.set('sigouts/1/amplitudes/7', q)
# 	_ , data = fsv.get_data()
# 	traces.append(data)

# traces = np.array(traces)
# plt.imshow(traces, aspect = 'auto')
# plt.show()
