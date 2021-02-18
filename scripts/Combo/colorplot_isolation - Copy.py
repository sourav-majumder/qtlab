import qt
from constants import *
from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
import numpy as np
import matplotlib.pyplot as plt
import time
import progressbar

def get_power():
	_ , power = fsv.get_max_freqs(1)
	return power[0]

def sideband_diff():
	qt.msleep(0.1)
	freqs, powers = fsv.get_max_freqs(2)
	powers = [power for _,power in sorted(zip(freqs,powers))]
	return powers[-1]-powers[0]

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
	# Coarse sweep
	i_arr = np.linspace(-12e-3, -24e-3, 12) # -18.49m
	q_arr = np.linspace(-18e-3, -30e-3, 12) # -24.24m
	opt_i, opt_q = dc_sweep(i_arr, q_arr, plot)
	# Fine sweep
	i_arr = np.linspace(opt_i-0.5e-3, opt_i+0.5e-3, 20)
	q_arr = np.linspace(opt_q-0.5e-3, opt_q+0.5e-3, 20)
	return dc_sweep(i_arr, q_arr, True)

def optimize_ph(ph_arr=np.linspace(-180, 180, 720), plot = False):
	# uhf.set('sigouts/1/amplitudes/7', 700e-3)
	# uhf.set('sigouts/0/amplitudes/3', 700e-3)
	uhf.set('demods/3/phaseshift', 0)
	fsv.set_span(100*MHz)
	fsv.set_bandwidth(5*kHz)
	fsv.set_sweep_points(20001)
	qt.msleep(1)
	fsv.markers_to_peaks(2)
	diffs = []
	import progressbar
	progress_bar = progressbar.ProgressBar(maxval=len(ph_arr), \
	    widgets=['Optimizing Phase ', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
	progress_bar.start()
	for index, phase in enumerate(ph_arr):
		uhf.set('demods/3/phaseshift', phase)
		diffs.append(sideband_diff())
		progress_bar.update(index+1)
	progress_bar.finish()
	diffs = np.array(diffs)
	indices = np.where(diffs == diffs.max())
	uhf.set('demods/3/phaseshift', ph_arr[indices[0][0]])
	if plot:
		plt.plot(ph_arr, diffs)
		plt.show()
	return ph_arr[indices[0][0]]

def optimize_phase(plot=False):
	ph_arr = np.linspace(-180, 180, 37)
	opt_ph = optimize_ph(ph_arr, plot)
	# Fine sweep
	ph_arr = np.linspace(opt_ph-10, opt_ph+10, 20)
	opt_ph = optimize_ph(ph_arr, plot)
	# Finer sweep
	ph_arr = np.linspace(opt_ph-1, opt_ph+1, 20)
	return optimize_ph(ph_arr, plot)

def optimize_amp(i_arr, q_arr, plot=False):
	diffs = []
	import progressbar
	progress_bar = progressbar.ProgressBar(maxval=len(i_arr), \
	    widgets=['Optimizing Amplitude', progressbar.Bar('.', '', ''), ' ', progressbar.Percentage(), ' (', progressbar.ETA(), ') '])
	progress_bar.start()
	for index, i in enumerate(i_arr):
		uhf.set('sigouts/0/amplitudes/3', i)
		diffs.append([])
		progress_bar.update(index+1)
		for q in q_arr:
			uhf.set('sigouts/1/amplitudes/7', q)
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

def optimize_amplitude(plot=False):
	i_arr = np.linspace(0, 700e-3, 10)
	q_arr = np.linspace(0, 700e-3, 10)
	opt_i, opt_q = optimize_amp(i_arr, q_arr, plot)
	# Fine sweep
	i_arr = np.linspace(opt_i-10e-3, opt_i+10e-3, 20)
	q_arr = np.linspace(opt_q-10e-3, opt_q+10e-3, 20)
	opt_i, opt_q = optimize_amp(i_arr, q_arr, plot)
	# Finer sweep
	i_arr = np.linspace(opt_i-0.5e-3, opt_i+0.5e-3, 20)
	q_arr = np.linspace(opt_q-0.5e-3, opt_q+0.5e-3, 20)
	return optimize_amp(i_arr, q_arr, True)

def optimize_all(plot=False):
	optimize_dc(plot=plot)
	uhf.set('sigouts/1/amplitudes/7', 700e-3)
	uhf.set('sigouts/0/amplitudes/3', 700e-3)
	optimize_phase(plot=plot)
	return optimize_amplitude(plot=plot)

def awg_program(samples, width_samples, i_amplitude, q_amplitude):
	awg_program_string = """
	//gauss(samples, amplitude, position, width)
	wave w1 = gauss(%d, 1, %f, %f);
	//sine(samples, amplitude, phaseOffset, nrOfPeriods)
	wave w2 = %s
	wave w3 = %s
	wave p1 = multiply(w1,w2);
	wave p2 = multiply(w1,w3);	
	while (true) {
	  playWave(p1,p2);
	  wait(3000);
	}""" % \
	(samples, float(samples)/2, width_samples,
		uhf.awg_sine(mix_freq, samples=samples, amplitude = i_amplitude),
		uhf.awg_sine(mix_freq, samples=samples, amplitude = q_amplitude))
	return awg_program_string

center_freq = 6.2*GHz
mix_freq = 37*MHz

fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS)
uhf = ZurichInstruments_UHFLI('dev2232') # Initializing UHFLI

opt_i, opt_q = optimize_all(True)
# opt_i, opt_q = 0.69271052631578955, 0.6287748538011696

uhf.setup_awg(awg_program(9000, 4500, opt_i/750e-3, opt_q/750e-3))
uhf.awg_on(single=False)


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
