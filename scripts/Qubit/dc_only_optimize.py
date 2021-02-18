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

def optimize_dc(center_freq,plot = False):
	fsv.set_centerfrequency(center_freq)
	fsv.set_span(2*MHz)
	fsv.set_bandwidth(10*kHz)
	fsv.set_sweep_points(1001)
	uhf.set('sigouts/0/offset', 0.0)
	uhf.set('sigouts/1/offset', 0.0)
	qt.msleep(1)
	fsv.marker_to_max()
	freq, power = fsv.get_max_freqs(1)
	# Very Coarse sweep
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

def set_device_settings(center_freq,vna_power=13):
#	uhf.extclk()
#	znb.set_external_reference(True)
	# znb.set_external_reference_frequency(10)
	# znb.set_sweep_type('cw')
	# znb.set_sweeptime(100000)
	# znb.set_center_frequency(center_freq)
	# znb.set_source_power(vna_power)
	# znb.add_trace('S21')
	# znb.rf_on()
	uhf.set('sigouts/0/on', 1)
	uhf.set('sigouts/1/on', 1)
	uhf.set('sigouts/0/enables/3', 0)
	uhf.set('sigouts/1/enables/7', 0)
	uhf.imp_50()

def optimize_all(center_freq,plot=False):
	set_device_settings(center_freq)
	return optimize_dc(center_freq,plot=plot)



center_freq = 5.821*GHz
# vna_power = 13

# znb = qt.instruments.create('ZNB20',	'RhodeSchwartz_ZNB20',	address = ZNB20_ADDRESS,	reset=True)
fsv = qt.instruments.create('FSV', 'RhodeSchwartz_FSV', address = FSV_ADDRESS, reset=True)
uhf = ZurichInstruments_UHFLI('dev2232') # Initializing UHFLI

# opt_i, opt_q = 0.69271052631578955, 0.6287748538011696
opt_i, opt_q = optimize_all(center_freq,True)