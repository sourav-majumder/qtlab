import scipy as sp
import numpy as np
import shutil
import matplotlib.pyplot as plt
import time
import progressbar
import qt

fac = sp.math.factorial

Hz = 1.
kHz = 1e3
MHz = 1e6
GHz = 1e9

s = 1.
ms = 1e-3
us = 1e-6
ns = 1e-9
ps = 1e-12

DEFAULT_SAMPLE_RATE_AWG_UHFLI = 1.8e9
DEFAULT_SAMPLE_RATE_SCOPE_UHFLI = 1.8e9

# DELL					PC			(Computer)				: 192.168.1.1
# Zurich Instruments	UHFLI		(Lock-in)				: 192.168.1.2
# Rhode & Schwartz		ZNB20		(VNA)					: 192.168.1.3
# Rhode & Schwartz		SMF100		(Signal Generator)		: 192.168.1.4
# Rigol					DP832A		(DC Power Supply)		: 192.168.1.5
# Rhode & Schwartz		RTE 1104	(Oscilloscope)			: 192.168.1.6
# AnaPico				APSYN 420	(LO Signal Generator)	: 192.168.1.7

PC_ADDRESS = 'TCPIP0::192.168.1.1::INSTR'
UHFLI_ADDRESS = 'TCPIP0::192.168.1.2::INSTR'
ZNB20_ADDRESS = 'TCPIP0::192.168.1.3::INSTR'
SMF100_ADDRESS = 'TCPIP0::192.168.1.4::INSTR'
DP832A_ADDRESS = 'TCPIP0::192.168.1.5::INSTR'
RTE_1104_ADDRESS = 'TCPIP0::192.168.1.6::INSTR'
APSYN420_ADDRESS = 'TCPIP0::192.168.1.7::INSTR'
FSV_ADDRESS = 'TCPIP0::192.168.1.8::INSTR'
GS200_ADDRESS = 'USB0::0x0B21::0x0039::91T416206::INSTR'

def create_instrument(name, ins_type, address=None, reset=False):
	if ins_type == 'ZurichInstruments_UHFLI':
		from ZurichInstruments_UHFLI import ZurichInstruments_UHFLI
		return ZurichInstruments_UHFLI(name, reset)
	elif address is None:
		raise Exception('Need an address for a qtlab instrument!!')
	else:
		import qt
		from visa import VisaIOError
		while True:
			try:
				ins = qt.instruments.create(name, ins_type, address=address, reset=reset)
				break
			except VisaIOError:
				print 'Falied. Trying again.'
		return ins

def reset_all_instruments():
	import qt
	for key, inst in qt.get_instruments().get_instruments().iteritems():
		inst.reset()

def copy_script(scriptname, dataname):
	#create script in data directory
    shutil.copy2('%s'%scriptname,'%s/%s'%(data.get_filepath()[:-(len(dataname)+11)],os.path.basename(scriptname)))

def filter_func(tc, order, t):
	wc=1/float(tc)
	return (wc*t)**(order-1)/fac(order-1)*wc*np.exp(-wc*t)

def ringdown_func(timearr, init_time, init_const, exp_const, tc, pulse_length):
	result = np.ones(len(timearr))*init_const
	resolution = timearr[1]-timearr[0]

	pstart_index = int(init_time/resolution)
	pstop_index = int((init_time + pulse_length)/resolution)
	if pstop_index >= len(timearr):
		pstop_index = len(timearr)-1
	if pstart_index >=len(timearr):
		pstart_index = len(timearr)-1
	result[pstart_index:pstop_index] = exp_const*exp_rise(np.linspace(0,pulse_length, pstop_index-pstart_index), tc)+init_const
	result[pstop_index:] = result[pstop_index-1]*exp_fall(np.linspace(0, timearr[-1]-timearr[0]-init_time-pulse_length, len(timearr)-pstop_index), tc)
	return result

def exp_fall(timearr, tc):
	return np.exp(-timearr/tc)

def exp_rise(timearr, tc):
	return 1-exp_fall(timearr, tc)

def deconvolve(data, tc, order):
	'''
	Returns deconvoluted data.
	'''
	t = data[0] # time values
	y = data[1] # recorded signal

	time = t[-1]-t[0]
	resolution = t[1]-t[0]

	if time <= 0:
		raise UHFLIException('Time must run forwards.')
	elif time < 10*tc:
		raise UHFLIException('Data must be longer than 10 time constants of the filter.')
	else:
		filt = filter_func(tc, order, np.arange(0, 10*tc, resolution))
		if filt.min() < 0e-5:
			raise UHFLIException('Filter error.')
		from scipy.signal import deconvolve
		return deconvolve(y,filt)

def get_power(fsv):
	_ , power = fsv.get_max_freqs(1)
	return power[0]

def dc_sweep(fsv, uhf, znb, i_arr, q_arr, plot = True):
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
			pow_arr[-1].append(get_power(fsv))
	progress_bar.finish()
	pow_arr = np.array(pow_arr)
	indices = np.where(pow_arr == pow_arr.min())
	uhf.set('sigouts/0/offset', i_arr[indices[0][0]])
	uhf.set('sigouts/1/offset', q_arr[indices[1][0]])
	if plot:
		plt.imshow(pow_arr, aspect='auto', extent=[q_arr[0], q_arr[-1], i_arr[-1], i_arr[-0]])
		plt.show()
	return i_arr[indices[0][0]],q_arr[indices[1][0]]

def optimize_dc(fsv, uhf, znb, center_freq,plot = False):
	fsv.set_centerfrequency(center_freq)
	fsv.set_span(2*MHz)
	fsv.set_bandwidth(10*kHz)
	fsv.set_sweep_points(3001)
	uhf.set('sigouts/0/offset', 0.0)
	uhf.set('sigouts/1/offset', 0.0)
	qt.msleep(1)
	fsv.marker_to_max()
	freq, power = fsv.get_max_freqs(1)
	# Very Coarse sweep
	i_arr = np.linspace(-500e-3, 500e-3, 50) # -18.49m
	q_arr = np.linspace(-500e-3, 500e-3, 50) # -24.24m
	opt_i, opt_q = dc_sweep(fsv, uhf, znb, i_arr, q_arr, plot)
	# Coarse sweep
	i_arr = np.linspace(opt_i-30e-3, opt_i+30e-3, 10)
	q_arr = np.linspace(opt_q-30e-3, opt_q+30e-3, 10)
	opt_i, opt_q = dc_sweep(fsv, uhf, znb, i_arr, q_arr, plot)
	# Fine sweep
	i_arr = np.linspace(opt_i-1e-3, opt_i+1e-3, 10)
	q_arr = np.linspace(opt_q-1e-3, opt_q+1e-3, 10)
	opt_i, opt_q = dc_sweep(fsv, uhf, znb, i_arr, q_arr, plot)
	# Finer sweep
	i_arr = np.linspace(opt_i-0.5e-3, opt_i+0.5e-3, 20)
	q_arr = np.linspace(opt_q-0.5e-3, opt_q+0.5e-3, 20)
	return dc_sweep(fsv, uhf, znb, i_arr, q_arr, plot)

def set_device_settings(fsv, uhf, znb, center_freq,vna_power=13):
	uhf.extclk()
	znb.reset()
	znb.set_external_reference(True)
	znb.set_external_reference_frequency(10)
	znb.set_sweep_type('cw')
	znb.set_sweeptime(100000)
	znb.set_center_frequency(center_freq)
	znb.set_source_power(vna_power)
	znb.add_trace('S21')
	znb.rf_on()
	uhf.set('awgs/0/enable', 0)
	uhf.set('sigouts/0/on', 1)
	uhf.set('sigouts/1/on', 1)
	uhf.set('sigouts/0/enables/3', 0)
	uhf.set('sigouts/1/enables/7', 0)
	uhf.imp_50()

def optimize_all(fsv, uhf, znb, center_freq,plot=True):
	set_device_settings(fsv, uhf, znb, center_freq)
	return optimize_dc(fsv, uhf, znb, center_freq,plot=plot)
