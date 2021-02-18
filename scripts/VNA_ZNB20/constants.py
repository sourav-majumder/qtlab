import scipy as sp
import numpy as np
import shutil

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